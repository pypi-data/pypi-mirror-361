def get_params(models):
    total_params = sum(param.numel() for param in models.parameters())
    trainable_params = sum(param.numel() for param in models.parameters() if param.requires_grad)

    return (total_params, trainable_params)