from sanic.log import logger

from .architecture.face.codeformer import CodeFormer
from .architecture.face.gfpganv1_clean_arch import GFPGANv1Clean
from .architecture.face.restoreformer_arch import RestoreFormer
from .architecture.HAT import HAT
from .architecture.LaMa import LaMa
from .architecture.MAT import MAT
from .architecture.OmniSR.OmniSR import OmniSR
from .architecture.RRDB import RRDBNet as ESRGAN
from .architecture.SPSR import SPSRNet as SPSR
from .architecture.SRVGG import SRVGGNetCompact as RealESRGANv2
from .architecture.SwiftSRGAN import Generator as SwiftSRGAN
from .architecture.Swin2SR import Swin2SR
from .architecture.SwinIR import SwinIR
from .types import PyTorchModel


class UnsupportedModel(Exception):
    pass


def load_state_dict(state_dict) -> PyTorchModel:
    logger.debug(f"Loading state dict into pytorch model arch")

    state_dict_keys = list(state_dict.keys())

    if "params_ema" in state_dict_keys:
        state_dict = state_dict["params_ema"]
    elif "params-ema" in state_dict_keys:
        state_dict = state_dict["params-ema"]
    elif "params" in state_dict_keys:
        state_dict = state_dict["params"]

    state_dict_keys = list(state_dict.keys())
    # SRVGGNet Real-ESRGAN (v2)
    if "body.0.weight" in state_dict_keys and "body.1.weight" in state_dict_keys:
        model = RealESRGANv2(state_dict)
    # SPSR (ESRGAN with lots of extra layers)
    elif "f_HR_conv1.0.weight" in state_dict:
        model = SPSR(state_dict)
    # Swift-SRGAN
    elif (
        "model" in state_dict_keys
        and "initial.cnn.depthwise.weight" in state_dict["model"].keys()
    ):
        model = SwiftSRGAN(state_dict)
    # HAT -- be sure it is above swinir
    elif "layers.0.residual_group.blocks.0.conv_block.cab.0.weight" in state_dict_keys:
        model = HAT(state_dict)
    # SwinIR
    elif "layers.0.residual_group.blocks.0.norm1.weight" in state_dict_keys:
        if "patch_embed.proj.weight" in state_dict_keys:
            model = Swin2SR(state_dict)
        else:
            model = SwinIR(state_dict)
    # GFPGAN
    elif (
        "toRGB.0.weight" in state_dict_keys
        and "stylegan_decoder.style_mlp.1.weight" in state_dict_keys
    ):
        model = GFPGANv1Clean(state_dict)
    # RestoreFormer
    elif (
        "encoder.conv_in.weight" in state_dict_keys
        and "encoder.down.0.block.0.norm1.weight" in state_dict_keys
    ):
        model = RestoreFormer(state_dict)
    elif (
        "encoder.blocks.0.weight" in state_dict_keys
        and "quantize.embedding.weight" in state_dict_keys
    ):
        model = CodeFormer(state_dict)
    # LaMa
    elif (
        "model.model.1.bn_l.running_mean" in state_dict_keys
        or "generator.model.1.bn_l.running_mean" in state_dict_keys
    ):
        model = LaMa(state_dict)
    # MAT
    elif "synthesis.first_stage.conv_first.conv.resample_filter" in state_dict_keys:
        model = MAT(state_dict)
    # Omni-SR
    elif (
        "total_ops" in state_dict_keys
        and "residual_layer.0.total_ops" in state_dict_keys
    ):
        model = OmniSR(state_dict)
    # Regular ESRGAN, "new-arch" ESRGAN, Real-ESRGAN v1
    else:
        try:
            model = ESRGAN(state_dict)
        except:
            # pylint: disable=raise-missing-from
            raise UnsupportedModel
    return model
