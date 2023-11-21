from config.models import DaasMetaConfig


def initial():
    meta_config = DaasMetaConfig.objects.all()
    if not meta_config:
        DaasMetaConfig.objects.create()
        