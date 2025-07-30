from collections import defaultdict
from typing import Dict, List, Literal, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn.functional as F
from jaxtyping import Bool, Float, Int
from scipy.optimize import linear_sum_assignment
from torch import Tensor, nn
from torch.cuda.amp import autocast
from warpconvnet.types import IterableTensor


# Comment types due to jit script
# def dice_loss(inputs: Float[Tensor, "Q N"], targets: Bool[Tensor, "T N"]) -> Float[Tensor, "Q T"]:  # type: ignore
@torch.jit.script
def dice_outter(inputs, targets):  # type: ignore
    """
    Compute the DICE loss, similar to generalized IOU for masks
    Args:
        inputs: A float tensor of arbitrary shape.
                The predictions for each example.
        targets: A bool mask tensor for each instance.
    """
    inputs = inputs.sigmoid()
    numerator = 2 * (inputs @ targets.T)
    # Q x T
    denominator = inputs.sum(1).view(-1, 1) + targets.sum(1).view(1, -1)
    loss = 1 - (numerator + 1) / (denominator + 1)
    return loss


# def dice_loss(input: Float[Tensor, "T N"], target: Bool[Tensor, "T N"]) -> Float[Tensor, "1"]:
@torch.jit.script
def dice_loss(
    inputs: torch.Tensor,
    targets: torch.Tensor,
):
    """
    Compute the DICE loss, similar to generalized IOU for masks
    Args:
        inputs: A float tensor of arbitrary shape.
                The predictions for each example.
        targets: A float tensor with the same shape as inputs. Stores the binary
                 classification label for each element in inputs
                (0 for the negative class and 1 for the positive class).
    """
    inputs = inputs.sigmoid()
    numerator = 2 * (inputs * targets).sum(1)
    denominator = inputs.sum(1) + targets.sum(1)
    loss = 1 - (numerator + 1) / (denominator + 1)
    return loss.mean()


# def sigmoid_ce_loss(inputs: Float[Tensor, "Q N"], targets: Bool[Tensor, "T N"]) -> Float[Tensor, "Q T"]:
@torch.jit.script
def sigmoid_ce_outter(inputs, targets, eps: float = 1e-8):  # type: ignore
    """
    Args:
        inputs: A float tensor of arbitrary shape.
                The predictions for each example.
        targets: A bool tensor for binary classification label
            for each element in inputs (0 for the negative class
            and 1 for the positive class).
    Returns:
        Loss tensor
    """
    N = inputs.shape[1]

    pos = F.binary_cross_entropy_with_logits(inputs, torch.ones_like(inputs), reduction='none')
    neg = F.binary_cross_entropy_with_logits(inputs, torch.zeros_like(inputs), reduction='none')

    loss = torch.einsum('nc,mc->nm', pos, targets) + torch.einsum('nc,mc->nm', neg, (1 - targets))

    return loss / N


# def sigmoid_ce_loss(inputs: Float[Tensor, "N T"], targets: Bool[Tensor, "N T"]) -> Float[Tensor, "1"]:
@torch.jit.script
def sigmoid_ce_loss(
    inputs: torch.Tensor,
    targets: torch.Tensor,
):
    """
    Args:
        inputs: A float tensor of arbitrary shape.
                The predictions for each example.
        targets: A float tensor with the same shape as inputs. Stores the binary
                 classification label for each element in inputs
                (0 for the negative class and 1 for the positive class).
    Returns:
        Loss tensor
    """
    loss = F.binary_cross_entropy_with_logits(inputs, targets, reduction="none")
    return loss.mean()


class HungarianMatcher(nn.Module):
    """This class computes an assignment between the targets and the predictions of the network

    For efficiency reasons, the targets don't include the no_object. Because of this, in general,
    there are more predictions than targets. In this case, we do a 1-to-1 matching of the best predictions,
    while the others are un-matched (and thus treated as non-objects).
    """

    def __init__(
        self,
        cost_class: float = 1,
        cost_mask: float = 1,
        cost_dice: float = 1,
    ):
        """Creates the matcher

        Params:
            cost_class: This is the relative weight of the classification error in the matching cost
            cost_mask: This is the relative weight of the focal loss of the binary mask in the matching cost
            cost_dice: This is the relative weight of the dice loss of the binary mask in the matching cost
        """
        super().__init__()
        self.cost_class = cost_class
        self.cost_mask = cost_mask
        self.cost_dice = cost_dice

    @torch.no_grad()
    def forward(
        self,
        pred_masks: Float[IterableTensor, "Q N"],
        target_bin_masks: Int[IterableTensor, "T N"],
        target_labels: Optional[Int[IterableTensor, "T"]] = None,  # noqa: F821
        logit_per_query: Optional[Float[IterableTensor, "Q C"]] = None,
    ) -> Tuple[List[Int[Tensor, "T 2"]], Dict[str, List[Tensor]]]:
        """
        Args:
            pred_masks: List of [Q x N] masks
            target_bin_masks: List of [T x N] binary masks
            target_labels: List of [T] labels
            logit_per_query: List of [Q x C] logits

        Returns:
            List of (T, 2) tensors, 0-th column for the query indices, 1-st column for the target indices
        """
        batch_size = len(pred_masks)

        indices = []
        costs = []
        # Iterate through batch size
        for b in range(batch_size):
            with autocast(enabled=False):
                out_mask = pred_masks[b].float()  # QxN
                tgt_mask = target_bin_masks[b].float()  # TxN
                # Compute the focal loss between masks
                cost_mask = sigmoid_ce_outter(out_mask, tgt_mask)
                # Compute the dice loss between masks
                cost_dice = dice_outter(out_mask, tgt_mask)

            # Final cost matrix
            C = self.cost_mask * cost_mask + self.cost_dice * cost_dice

            if target_labels is not None:
                # Compute the classification cost. Contrary to the loss, we don't use the NLL,
                # but approximate it in 1 - proba[target class].
                # The 1 is a constant that doesn't change the matching, it can be omitted.
                out_prob = logit_per_query[b].softmax(-1)
                tgt_ids = target_labels[b].clone()
                filter_ignore = tgt_ids == 253
                tgt_ids[filter_ignore] = 0
                cost_class = -out_prob[:, tgt_ids]
                cost_class[:, filter_ignore] = -1.0
                C += self.cost_class * cost_class

            C = C.cpu().numpy()
            indices.append(torch.as_tensor(linear_sum_assignment(C)))
            # Select the final cost
            costs.append(C[indices[b][0], indices[b][1]].mean())

        final_cost = torch.tensor(costs)
        return indices, final_cost


class SetCriterion(nn.Module):
    def __init__(
        self,
        losses: List[Literal["class", "mask"]] = ["mask"],
        num_classes: Optional[int] = None,
        cost_class: float = 1,
        cost_mask: float = 1,
        cost_dice: float = 1,
    ):
        """Create the criterion.
        Parameters:
            num_classes: number of object categories, omitting the special no-object category
            matcher: module able to compute a matching between targets and proposals
            eos_coef: relative classification weight applied to the non-object category
            losses: list of all the losses to be applied. See get_loss for list of available losses.
        """
        super().__init__()
        assert num_classes is not None if "labels" in losses else True
        self.num_classes = num_classes
        self.matcher = HungarianMatcher(
            cost_class=cost_class, cost_mask=cost_mask, cost_dice=cost_dice
        )
        self.losses = losses

    def loss_mask_dice(
        self,
        pred_masks: List[Float[Tensor, "Q N"]],
        target_bin_masks: List[Bool[Tensor, "T N"]],
        match_indices: List[Int[Tensor, "T 2"]],
    ):
        loss_masks = 0
        loss_dices = 0
        batch_size = len(match_indices)
        for batch_id, (map_id, target_id) in enumerate(match_indices):
            pred_masks_sel = pred_masks[batch_id][map_id]
            target_masks_sel = target_bin_masks[batch_id][target_id]
            target_masks_sel = target_masks_sel.float()
            loss_masks += sigmoid_ce_loss(pred_masks_sel, target_masks_sel)
            loss_dices += dice_loss(pred_masks_sel, target_masks_sel)

        return {
            "mask": loss_masks / batch_size,
            "dice": loss_dices / batch_size,
        }

    def forward(
        self,
        pred_masks: List[Float[Tensor, "N Q"]],
        target_bin_masks: List[
            Union[Int[Tensor, "N"], Bool[Tensor, "T N"]]  # noqa: F821
        ],
    ) -> Tuple[Dict[str, Tensor], Tensor]:
        """This performs the loss computation.
        Parameters:
             pred_masks: list of [Q x N] masks
             target_bin_masks: list of [T x N] binary masks
             match_indices: list of (T, 2) tensors, 0-th column for the query indices, 1-st column for the target indices
        """
        if target_bin_masks[0].dtype != torch.bool or target_bin_masks[0].ndim == 1:
            # Given the target labels, convert to binary masks
            target_bin_masks = label_to_bin_mask(target_bin_masks)

        match_indices, final_cost = self.matcher(pred_masks, target_bin_masks)

        # Compute all the requested losses
        losses = {}
        for loss in self.losses:
            if loss == "class":
                raise NotImplementedError("labels loss is not implemented")
            elif loss == "mask":
                losses.update(
                    self.loss_mask_dice(pred_masks, target_bin_masks, match_indices)
                )
            else:
                raise NotImplementedError(f"{loss} loss is not implemented")
        return losses, final_cost.mean()


def dict_collate_fn(batch: List[Dict]):
    return {
        k: [
            torch.tensor(item[k]) if isinstance(item[k], np.ndarray) else item[k]
            for item in batch
        ]
        for k in batch[0].keys()
    }


def label_to_bin_mask(
    labels: Int[IterableTensor, "N"],  # noqa: F821
) -> List[Bool[Tensor, "T N"]]:
    # Convert the target int to binary masks
    target_masks = []
    batch_size = (
        labels.size(0)
        if isinstance(labels, Tensor) and labels.is_nested
        else len(labels)
    )
    for b in range(batch_size):
        # Map all negative or invalid labels to -1
        curr_labels = labels[b].clone()
        curr_labels[curr_labels < 0] = -1
        curr_labels[curr_labels >= 253] = -1
        curr_labels += 1
        target_unique = torch.unique(curr_labels).cpu()
        max_target = target_unique.max().item()
        # assert that they are consecutive integers
        # 0-th row will be truncated
        targets_masks = torch.zeros(
            max_target + 1,
            len(labels[b]),
            dtype=torch.bool,
            device=labels[0].device,
        )
        targets_masks[curr_labels, torch.arange(len(curr_labels))] = 1
        if not torch.all(torch.arange(len(target_unique)) == target_unique):
            # Remove targets that is not consecutive integers
            # Set intersection of range(max_target) and target_unique
            intersection = set(range(max_target)) & set(target_unique.tolist())
            targets_masks = targets_masks[list(intersection)]
        else:
            # Remove the 0-th row
            targets_masks = targets_masks[1:]
        target_masks.append(targets_masks)
    return target_masks


if __name__ == "__main__":
    from warpconvnet.models.internal.scripts.datasets.scannet_inst_dataset import (
        ScanNet200Dataset,
    )

    dataset = ScanNet200Dataset(
        split="train",
        data_root="/datasets/scannet_hf",
    )
    # Print key: shape, unique values if it is int
    for k, v in dataset[0].items():
        print(
            k,
            v.shape if hasattr(v, "shape") else v,
            (
                np.unique(v)
                if isinstance(v, np.ndarray) and v.dtype in [np.int64, np.int32]
                else ""
            ),
        )
    # coord (166873, 3)
    # color (166873, 3)
    # normal (166873, 3)
    # name scene0223_01
    # segment (166873,) [ -1   0   2   4   7   8   9  10  14  35  48  80  81  83  85 172]
    # instance (166873,) [-1  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22
    # 23 24]

    # collate 2 dataset items
    batch = dict_collate_fn([dataset[0], dataset[1]])

    # Create a dummy prediction
    B, C = 2, 256
    Ns = [len(c) for c in batch["coord"]]
    Q = 100  # number of queries
    query_feats = torch.randn(B, Q, C)
    out_feats = [torch.randn(N, C) for N in Ns]
    out_masks = [query @ feat.T for query, feat in zip(query_feats, out_feats)]  # QxN
    target_bin_masks = label_to_bin_mask(batch["instance"])
    matcher = HungarianMatcher(cost_class=1, cost_mask=1, cost_dice=1)
    indices, costs = matcher.forward(out_masks, target_bin_masks)

    # Compute the loss
    criterion = SetCriterion(losses=["mask"])
    print(criterion)
    losses, match_cost = criterion(out_masks, batch["instance"])
    print(losses)
    print(match_cost)
