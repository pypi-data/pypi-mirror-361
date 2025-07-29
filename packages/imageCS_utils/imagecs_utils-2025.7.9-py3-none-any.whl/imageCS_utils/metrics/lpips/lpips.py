import torch
import lpips

class LPIPS:
    def __init__(self, net, device=torch.device("cpu")):
        """
        net = "alex" or "vgg"
        """
        assert net in ["alex", "vgg"]
        self.metrics = lpips.LPIPS(net=net).to(device)
        self.dev = device
    
    def _norm(self, img:torch.Tensor):
        img = img * 2 - 1
        return img
    
    def _to_4d_RGB_Tensor(self, img:torch.Tensor):
        img_size = img.size()

        # To 4-D Tensor
        assert len(img_size) in [3, 4], f"Image Size must be 3-D or 4-D, But get {len(img_size)}-D here."
        if len(img_size) == 3:
            img = img.unsqueeze(0)
        
        # To RGB Tensor
        assert img.size(1) in [1, 3], f"Image must have 1 channel or 3 channels, but get {img.size(1)} channel(s)."
        if img.size(1) == 1:
            img = img.repeat(1, 3, 1, 1)
        
        return img
    
    def _pre_prosses(self, img:torch.Tensor):
        img = img.to(self.dev)
        img = self._norm(img)
        img = self._to_4d_RGB_Tensor(img)
        return img
    
    def lpips(self, img1:torch.Tensor, img2:torch.Tensor):
        img1 = self._pre_prosses(img1)
        img2 = self._pre_prosses(img2)
        with torch.no_grad():
            data = self.metrics(img1, img2)
        return data
