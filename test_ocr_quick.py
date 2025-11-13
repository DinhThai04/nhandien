"""Script kiểm tra nhanh OCR với ảnh thực tế"""

from src.ocr_engine import OCREngine
from src.image_processor import ImageProcessor
from src.region_classifier import RegionClassifier
import cv2

print("=" * 60)
print("KIỂM TRA OCR VỚI ẢNH THỰC TẾ")
print("=" * 60)

# Đọc ảnh
image_path = "1118b756-26da-4df5-b146-97830da3326b.jpg"
print(f"\n📷 Đọc ảnh: {image_path}")
img = cv2.imread(image_path)

if img is None:
    print("❌ Không thể đọc ảnh!")
    exit(1)

print(f"✅ Kích thước ảnh: {img.shape[1]}x{img.shape[0]} pixels")

# Tiền xử lý ảnh
print("\n🔧 Tiền xử lý ảnh...")
processor = ImageProcessor()
img_processed = processor.preprocess_image(img, method='auto')
print("✅ Hoàn thành tiền xử lý")

# Nhận dạng văn bản
print("\n📝 Nhận dạng văn bản...")
ocr = OCREngine()
result = ocr.extract_text_with_confidence(img_processed)

print("\n" + "=" * 60)
print("KẾT QUẢ OCR")
print("=" * 60)
print(f"\n📊 Độ tin cậy: {result['confidence']:.2f}%")
print(f"\n📄 Văn bản nhận dạng được:")
print("-" * 60)
if result['text']:
    print(result['text'])
else:
    print("(Không nhận dạng được văn bản)")
print("-" * 60)

# Trích xuất thông tin có cấu trúc
if result['text']:
    print("\n🔍 Trích xuất thông tin...")
    structured = ocr.extract_structured_data(result['text'])
    
    print("\n📱 Số điện thoại:", structured.get('phone_numbers', []))
    print("📮 Mã bưu chính:", structured.get('postal_codes', []))
    print("📍 Địa chỉ:", structured.get('addresses', '')[:200] + "..." if len(structured.get('addresses', '')) > 200 else structured.get('addresses', ''))

# Phân loại khu vực
if result['text']:
    print("\n🗺️  Phân loại khu vực...")
    classifier = RegionClassifier()
    region_result = classifier.classify(result['text'])
    
    print(f"\n✅ Khu vực: {region_result['region_name']}")
    print(f"   Độ tin cậy: {region_result['confidence']:.2f}%")
    if region_result['province']:
        print(f"   Tỉnh/Thành: {region_result['province']}")
    if region_result['matched_keywords']:
        print(f"   Từ khóa: {', '.join(region_result['matched_keywords'][:5])}")

print("\n" + "=" * 60)
