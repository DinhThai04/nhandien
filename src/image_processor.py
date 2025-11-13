"""
Module xử lý ảnh trước khi OCR
"""
import cv2
import numpy as np
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageProcessor:
    """Xử lý ảnh để tăng độ chính xác của OCR"""
    
    def __init__(self):
        self.logger = logger
    
    def preprocess_image(self, image_path: str, method: str = 'auto') -> np.ndarray:
        """
        Tiền xử lý ảnh trước khi OCR
        
        Args:
            image_path: Đường dẫn đến ảnh hoặc numpy array của ảnh
            method: Phương pháp xử lý ('auto', 'grayscale', 'threshold', 'denoise')
        
        Returns:
            np.ndarray: Ảnh đã được xử lý
        """
        try:
            # Đọc ảnh nếu là đường dẫn, hoặc dùng trực tiếp nếu là numpy array
            if isinstance(image_path, str):
                image = cv2.imread(image_path)
                if image is None:
                    raise ValueError(f"Không thể đọc ảnh từ {image_path}")
            else:
                # Đã là numpy array
                image = image_path
            
            self.logger.info(f"Đọc ảnh thành công: {image_path}")
            
            if method == 'auto':
                # Tự động chọn phương pháp xử lý tốt nhất
                processed = self._auto_process(image)
            elif method == 'grayscale':
                processed = self._convert_to_grayscale(image)
            elif method == 'threshold':
                processed = self._apply_threshold(image)
            elif method == 'denoise':
                processed = self._denoise(image)
            else:
                processed = image
            
            return processed
        
        except Exception as e:
            self.logger.error(f"Lỗi xử lý ảnh: {e}")
            raise
    
    def _auto_process(self, image: np.ndarray) -> np.ndarray:
        """Tự động xử lý ảnh với pipeline tối ưu"""
        # Chuyển sang grayscale
        gray = self._convert_to_grayscale(image)
        
        # Giảm nhiễu
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Tăng contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Adaptive threshold
        thresh = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations để làm sạch
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def _convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Chuyển ảnh sang grayscale"""
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    
    def _apply_threshold(self, image: np.ndarray) -> np.ndarray:
        """Áp dụng threshold để làm rõ text"""
        gray = self._convert_to_grayscale(image)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
    
    def _denoise(self, image: np.ndarray) -> np.ndarray:
        """Giảm nhiễu trong ảnh"""
        if len(image.shape) == 3:
            return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        else:
            return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
    
    def resize_image(self, image: np.ndarray, max_width: int = 1920, 
                     max_height: int = 1080) -> np.ndarray:
        """
        Resize ảnh nếu quá lớn
        
        Args:
            image: Ảnh cần resize
            max_width: Chiều rộng tối đa
            max_height: Chiều cao tối đa
        
        Returns:
            np.ndarray: Ảnh đã được resize
        """
        height, width = image.shape[:2]
        
        if width <= max_width and height <= max_height:
            return image
        
        # Tính tỷ lệ resize
        ratio = min(max_width / width, max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        resized = cv2.resize(image, (new_width, new_height), 
                           interpolation=cv2.INTER_AREA)
        
        self.logger.info(f"Resize ảnh từ {width}x{height} xuống {new_width}x{new_height}")
        return resized
    
    def rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """
        Xoay ảnh theo góc cho trước
        
        Args:
            image: Ảnh cần xoay
            angle: Góc xoay (độ)
        
        Returns:
            np.ndarray: Ảnh đã được xoay
        """
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (width, height),
                                flags=cv2.INTER_CUBIC,
                                borderMode=cv2.BORDER_REPLICATE)
        
        return rotated
    
    def detect_and_correct_skew(self, image: np.ndarray) -> np.ndarray:
        """
        Phát hiện và sửa độ nghiêng của ảnh
        
        Args:
            image: Ảnh cần sửa
        
        Returns:
            np.ndarray: Ảnh đã được sửa nghiêng
        """
        try:
            # Chuyển sang grayscale
            gray = self._convert_to_grayscale(image)
            
            # Áp dụng threshold
            _, binary = cv2.threshold(gray, 0, 255, 
                                    cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Tìm các điểm không phải background
            coords = np.column_stack(np.where(binary > 0))
            
            # Tính góc nghiêng
            angle = cv2.minAreaRect(coords)[-1]
            
            # Điều chỉnh góc
            if angle < -45:
                angle = 90 + angle
            elif angle > 45:
                angle = angle - 90
            
            # Xoay ảnh nếu góc nghiêng đáng kể
            if abs(angle) > 0.5:
                self.logger.info(f"Sửa độ nghiêng: {angle:.2f} độ")
                return self.rotate_image(image, angle)
            
            return image
        
        except Exception as e:
            self.logger.warning(f"Không thể sửa độ nghiêng: {e}")
            return image
    
    def crop_border(self, image: np.ndarray, border_size: int = 10) -> np.ndarray:
        """
        Cắt bỏ viền ảnh
        
        Args:
            image: Ảnh cần cắt
            border_size: Kích thước viền cần cắt (pixels)
        
        Returns:
            np.ndarray: Ảnh đã được cắt viền
        """
        height, width = image.shape[:2]
        
        if height <= 2 * border_size or width <= 2 * border_size:
            return image
        
        return image[border_size:height-border_size, 
                    border_size:width-border_size]
    
    def save_processed_image(self, image: np.ndarray, output_path: str) -> None:
        """
        Lưu ảnh đã xử lý
        
        Args:
            image: Ảnh cần lưu
            output_path: Đường dẫn lưu ảnh
        """
        try:
            cv2.imwrite(output_path, image)
            self.logger.info(f"Đã lưu ảnh xử lý tại: {output_path}")
        except Exception as e:
            self.logger.error(f"Lỗi khi lưu ảnh: {e}")
            raise


if __name__ == "__main__":
    # Test
    processor = ImageProcessor()
    print("ImageProcessor module loaded successfully!")
