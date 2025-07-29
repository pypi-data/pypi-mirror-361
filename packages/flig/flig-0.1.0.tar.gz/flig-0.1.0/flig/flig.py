import torch
import numpy as np
from typing import Union, Optional, Any
from captum.attr import IntegratedGradients

class FFTModelWrapper(torch.nn.Module):
    def __init__(self, model, input_full=None, start_idx=None, n_steps=50):
        super().__init__()
        self.model = model
        self.input_full = input_full
        self.start_idx = start_idx
        self.n_steps = n_steps

    def forward(self, inp: torch.Tensor, *args) -> torch.Tensor:
        if self.input_full is None:
            # Full input processing
            return self.model(torch.fft.irfft(inp, dim=-1), *args)

        # Segment processing
        seg = torch.fft.irfft(inp, dim=-1)
        seg_length = seg.shape[-1]

        # Prepare batch dimension
        seg = seg.view(self.n_steps, 1, seg_length)
        x_full = self.input_full.repeat(self.n_steps, 1, 1)

        # Calculate insertion bounds
        lower = self.start_idx
        upper = lower + seg_length

        # Create interpolation alphas
        alphas = torch.linspace(0, 1, self.n_steps, device=x_full.device)
        alphas = alphas.view(-1, 1, 1)

        # Apply alpha scaling and insert segment
        x_full = x_full * alphas
        x_full[:, :, lower:upper] = seg

        return self.model(x_full, *args)

def attribute(
        input: Union[np.ndarray, list, torch.Tensor],
        model: Any,
        target: Optional[int] = None,
        baseline: Optional[Union[np.ndarray, list, torch.Tensor]] = None,
        n_steps: int = 50,
        segment: Optional[Union[np.ndarray, list, torch.Tensor]] = None,
        start_idx: Optional[int] = None,
        additional_forward_args: Optional[Any] = None
) -> np.ndarray:
    """
    Compute frequency-domain attributions with unified input handling

    Args:
        input: Full time-series input (1D or 2D array-like)
        model: Loaded model instance
        target: Target output index
        baseline: Reference baseline input
        n_steps: Number of integration steps
        segment: Optional signal segment for partial analysis
        start_idx: Start index of segment in full input

    Returns:
        Attribution scores as numpy array
    """
    # Unified input handling
    input_primary = segment if segment is not None else input
    input_primary = torch.as_tensor(input_primary, dtype=torch.float32)


    input_primary = input_primary.unsqueeze(0)

    print(f'DEBUG: input_primary: {input_primary.shape}')
    # Validate segment position
    if segment is not None:
        if start_idx is None:
            raise ValueError("start_idx required for segment analysis")
        if start_idx + input_primary.shape[-1] > input.shape[-1]:
            raise ValueError("Segment exceeds original input length")

    # Baseline handling
    if baseline is None:
        baseline = torch.zeros_like(input_primary)
    else:
        baseline = torch.as_tensor(baseline, dtype=torch.float32)
        if baseline.shape != input_primary.shape:
            raise ValueError(f"Baseline shape {baseline.shape} must match "
                             f"primary input shape {input_primary.shape}")

    # Device setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    input_primary = input_primary.to(device)
    baseline = baseline.to(device)
    input_full = torch.as_tensor(input, dtype=torch.float32).to(device)

    # Model wrapping
    wrapper_params = {
        'model': model,
        'n_steps': n_steps,
        'input_full': input_full.unsqueeze(0) if input_full.ndim == 1 else input_full,
        'start_idx': start_idx
    } if segment is not None else {'model': model}

    wrapped_model = FFTModelWrapper(**wrapper_params).to(device).eval()

    # FFT transformation
    fft_input = torch.fft.rfft(input_primary, dim=-1)
    fft_baseline = torch.fft.rfft(baseline, dim=-1)

    # Attribution calculation
    ig = IntegratedGradients(wrapped_model)
    attr = ig.attribute(fft_input,
                        target=target,
                        baselines=fft_baseline,
                        n_steps=n_steps,
                        additional_forward_args=additional_forward_args,)

    return attr.detach().cpu().numpy().squeeze().real