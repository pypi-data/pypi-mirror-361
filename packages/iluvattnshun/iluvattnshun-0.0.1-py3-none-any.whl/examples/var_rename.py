"""Variable renaming datagen and training w/ pre-LN transformer."""

import string
from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import LinearLR

from iluvattnshun.nn import MultilayerTransformer
from iluvattnshun.prompter import PromptConfig, Prompter
from iluvattnshun.trainer import Trainer, TrainerConfig
from iluvattnshun.types import TensorTree

MASK_TOKEN = "."
MASK_ID = 38


@dataclass
class VariableRenamingConfig(PromptConfig, TrainerConfig):
    """Configuration for variable renaming prompts."""

    # model
    num_layers: int
    """Number of transformer layers."""
    dim_model: int
    """Dimension of the model."""
    num_heads: int
    """Number of attention heads."""
    dropout_attn: float
    """Dropout rate for the attention layer."""
    dropout_mlp: float
    """Dropout rate for the MLP layer."""
    dropout_emb: float
    """Dropout rate for the embedding layer."""
    rope_base: float
    """Base for the Rope positional encoding."""

    # training
    learning_rate: float
    """Learning rate."""
    weight_decay: float
    """Weight decay."""
    warmup_steps: int
    """Number of batches until the learning rate is warmed up."""
    lr_start_factor: float
    """What to multiply the learning rate by at the start of warmup."""

    # data generation
    num_chains: int
    """Number of independent renaming chains."""
    num_renames: int
    """Number of renames per example."""
    train_size: int
    """Number of training examples."""
    test_size: int
    """Number of test examples."""
    dataset_path: str
    """Path to the dataset."""

    def data_hash_params(self) -> list[str]:
        return ["num_chains", "num_renames", "train_size", "test_size"]


class VariableRenamingPrompter(Prompter[VariableRenamingConfig]):
    """Prompter for generating variable renaming exercises.

    Generates prompts where variables are renamed in chains, and the task
    is to evaluate the final variable in terms of the initial value.
    """

    def get_prompt(self, rng: np.random.Generator) -> tuple[str, str, dict[str, Any]]:
        """Samples a variable renaming prompt and answers.

        Example prompt: "1>a;2>b;a>c;b>d;d>e;"
        Answers:        "1.1.2.2.1.1.2.2.2.2." where "." means <MASK>
        Depths:         "00000000111111112222"

        When redefining, only sample from variables which are not currently at
        the end of any chain (no DAG structure).

        Since evaluations are single digit, we can only have at most 10 chains.

        We also store the depth at each prediction step for eval purposes.
        """
        num_chains = self.config.num_chains
        assert num_chains <= 10, "We don't support more than 10 chains."

        # initialize evaluations and state trackers
        evals = np.arange(num_chains)
        rng.shuffle(evals)
        eval_strs = [str(int(e)) for e in evals]
        eval_depths = [0] * num_chains
        current_vars = eval_strs.copy()

        # track the active variable of each chain for membership checks
        active_vars = set(current_vars)

        # prepare for prompt and answer parts
        prompt_parts: list[str] = []
        answer_parts: list[str] = []
        depth_parts: list[int] = []

        # precompute available letters
        letters = list(string.ascii_lowercase)

        for _ in range(self.config.num_renames):
            chain_idx = rng.integers(0, num_chains)

            # choose a new variable not currently active in any chain
            choices = [c for c in letters if c not in active_vars]
            new_var = str(rng.choice(choices))
            old_var = current_vars[chain_idx]

            # keeping same lengths for simplicity downstream
            prompt_parts.append(f"{old_var}>{new_var};")
            answer_parts.append(f"{eval_strs[chain_idx]}.{eval_strs[chain_idx]}.")
            depth_parts.extend([eval_depths[chain_idx]] * 4)

            # update active variables and state trackers
            active_vars.remove(old_var)
            active_vars.add(new_var)
            current_vars[chain_idx] = new_var
            eval_depths[chain_idx] += 1

        return "".join(prompt_parts), "".join(answer_parts), {"depths": depth_parts}

    @property
    def _tokenization_map(self) -> dict[str, int]:
        char_to_token: dict[str, int] = {}
        for i in range(10):
            char_to_token[str(i)] = i
        for c in "abcdefghijklmnopqrstuvwxyz":
            char_to_token[c] = ord(c) - ord("a") + 10
        char_to_token[">"] = 36
        char_to_token[";"] = 37
        char_to_token["."] = 38
        return char_to_token

    def tokenize(self, text: str) -> list[int]:
        """Tokenize the input text.

        Maps:
        - Numbers 0-9 -> tokens 0-9
        - Letters a-z -> tokens 10-35
        - '>' -> token 36
        - ';' -> token 37
        - '.' -> token 38 (mask)
        """
        tokens = []
        for c in text:
            tokens.append(self._tokenization_map[c])
        return tokens

    def detokenize(self, tokens: list[int]) -> str:
        """Detokenize the input tokens.

        Maps:
        - Tokens 0-9 -> Numbers 0-9
        - Tokens 10-35 -> Letters a-z
        - Tokens 36-37 -> '>', ';'
        - Token 38 -> '.' (mask)
        """
        inverse_tokenization_map: dict[int, str] = {v: k for k, v in self._tokenization_map.items()}
        return "".join([inverse_tokenization_map[token] for token in tokens])


class VariableRenamingTrainer(Trainer[VariableRenamingConfig]):
    """Training decoder-only transformer for variable renaming."""

    def init_state(self) -> None:
        """Adding datasets and tokenizers to the trainer state."""
        self.prompter = VariableRenamingPrompter(self.config)
        self.ds_dict = self.prompter.make_dataset(
            self.config.dataset_path,
            train_size=self.config.train_size,
            test_size=self.config.test_size,
            seed=42,
        )
        self.ds_dict.set_format(type="torch", columns=["prompt_tokens", "answer_tokens", "prompt", "answer", "depths"])

        # log train test stats
        train_prompts = set(self.ds_dict["train"]["prompt"])
        test_prompts = set(self.ds_dict["test"]["prompt"])
        train_total = len(self.ds_dict["train"])
        train_unique = len(train_prompts)
        train_duplicates = train_total - train_unique
        overlap_with_train = test_prompts.intersection(train_prompts)
        self.logger.log_text(
            "train_test_stats.txt",
            f"[Train Set] Total: {train_total}, Unique: {train_unique}, Duplicates: {train_duplicates}\n"
            f"[Test Set] {len(overlap_with_train)} out of {len(test_prompts)} are also in the train set.",
        )

    def get_model(self) -> nn.Module:
        """Get the model."""
        model = MultilayerTransformer(
            vocab_size=39,
            d_model=self.config.dim_model,
            n_heads=self.config.num_heads,
            n_layers=self.config.num_layers,
            rope_base=self.config.rope_base,
            dropout_attn=self.config.dropout_attn,
            dropout_mlp=self.config.dropout_mlp,
            dropout_emb=self.config.dropout_emb,
        )
        return model

    def get_optimizer(self, model: nn.Module) -> optim.Optimizer:
        """Returns a basic Adam optimizer."""
        return optim.AdamW(model.parameters(), lr=self.config.learning_rate, weight_decay=self.config.weight_decay)

    def get_scheduler(self, optimizer: optim.Optimizer) -> LinearLR | None:
        """Returns a learning rate scheduler."""
        if self.config.warmup_steps == 0:
            return None

        scheduler = LinearLR(
            optimizer, start_factor=self.config.lr_start_factor, end_factor=1.0, total_iters=self.config.warmup_steps
        )
        return scheduler

    def get_loss(self, model: nn.Module, batch: TensorTree) -> tuple[torch.Tensor, torch.Tensor]:
        """Returns the cross-entropy loss over the final token logits.

        Example prompt and answer (where . is masked out):
            Prompt:  ";1>a;2>b;a>c;b>d"
            Mask:    "0101010101010101"
            Answers: " 1 1 2 2 1 1 2 2"
        """
        x = batch["prompt_tokens"]  # (batch, seq)
        y = batch["answer_tokens"]  # (batch, seq)
        mask = (y != MASK_ID).long()  # (batch, seq)

        logits, _, _, _ = model(x)  # (batch, seq, vocab_size)
        vocab_size = logits.shape[-1]

        # flatten for masked loss computation
        logits_flat = logits.view(-1, vocab_size)  # (batch*seq, vocab_size)
        y_flat = y.view(-1)  # (batch*seq)
        mask_flat = mask.view(-1).bool()  # (batch*seq)

        # get cross-entropy loss over masked positions
        logits_masked = logits_flat[mask_flat]  # (n, vocab_size)
        y_masked = y_flat[mask_flat]  # (n)
        loss = torch.nn.functional.cross_entropy(logits_masked, y_masked)

        return loss, logits

    def val_metrics(self, model: nn.Module, batch: TensorTree, preds: torch.Tensor) -> dict[str, float | str]:
        """Get additional validation metrics for a batch."""
        predicted_answers = preds.argmax(dim=-1)  # (batch, seq)
        target = batch["answer_tokens"].to(predicted_answers.device)  # (batch, seq)
        mask = target != MASK_ID  # (batch, seq)

        correct = ((predicted_answers == target) & mask).float()
        total_accuracy = correct.sum() / mask.sum()

        # Compute per-depth accuracy
        depth_tensor = batch["depths"].to(predicted_answers.device)  # (batch, seq)
        depth_metrics = {}
        for depth_val in torch.unique(depth_tensor[mask]):
            depth_mask = (depth_tensor == depth_val) & mask
            correct_at_depth = ((predicted_answers == target) & depth_mask).float()
            acc = correct_at_depth.sum() / depth_mask.sum()
            depth_metrics[f"acc_per_depth/{int(depth_val)}"] = acc.item()

        # Sample decoding info
        sample_idx = 0
        sample_prompt = batch["prompt"][sample_idx]
        sample_answer = batch["answer"][sample_idx]
        sample_pred_token_ids = predicted_answers[sample_idx].tolist()
        predicted_answer = self.prompter.detokenize(sample_pred_token_ids)
        correct_str = "".join(
            "." if sample_answer[i] == MASK_TOKEN else "✓" if sample_answer[i] == predicted_answer[i] else "✗"
            for i in range(len(sample_answer))
        )

        return {
            "sample_prompt": sample_prompt,
            "sample_answer": sample_answer,
            "sample_pred": predicted_answer,
            "sample_correct": correct_str,
            "accuracy": total_accuracy.item(),
            **depth_metrics,
        }

    def get_train_dataloader(self) -> Iterable[TensorTree]:
        """Get the train dataloader."""
        return torch.utils.data.DataLoader(
            self.ds_dict["train"],
            batch_size=self.config.batch_size,
            shuffle=True,
            prefetch_factor=4,
            num_workers=4,
        )

    def get_val_dataloader(self) -> Iterable[TensorTree]:
        """Get the val dataloader."""
        return torch.utils.data.DataLoader(
            self.ds_dict["test"],
            batch_size=self.config.batch_size,
            shuffle=False,
            prefetch_factor=4,
            num_workers=4,
        )


if __name__ == "__main__":
    # Example usage (config gets overridden by CLI args):
    # python -m examples.var_rename --num_layers=3 --overwrite_existing_checkpoints
    config = VariableRenamingConfig(
        num_layers=8,
        dim_model=128,
        num_heads=4,
        dropout_attn=0.0,
        dropout_mlp=0.1,
        dropout_emb=0.1,
        rope_base=2000.0,
        train_size=1_000_000,  # Ideally larger when we speed up generation
        test_size=10_000,
        num_chains=4,
        num_renames=150,
        learning_rate=1e-4,
        weight_decay=1e-2,
        batch_size=128,
        num_epochs=1000,
        warmup_steps=4000,
        lr_start_factor=1e-3,  # results in 1e-7 starting lr
        eval_every_n_samples=1_000_000,
        log_every_n_seconds=3,
        dataset_path="data/var_rename",
        tensorboard_logdir="logs/var_rename",
        save_every_n_seconds=100,
        overwrite_existing_checkpoints=True,
    )
    trainer = VariableRenamingTrainer(config)
    trainer.run()
