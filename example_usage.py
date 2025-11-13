"""
File ví dụ sử dụng các modules của ứng dụng OCR
"""
import sys
from pathlib import Path

# Thêm thư mục gốc vào path
sys.path.append(str(Path(__file__).parent))

from src.ocr_engine import OCREngine
from src.region_classifier import RegionClassifier
from src.image_processor import ImageProcessor


def example_basic_usage():
    """Ví dụ cơ bản sử dụng OCR"""
    print("=" * 50)
    print("VÍ DỤ 1: Sử dụng cơ bản")
    print("=" * 50)
    
    # Khởi tạo các module
    ocr = OCREngine()
    classifier = RegionClassifier()
    processor = ImageProcessor()
    
    # Đường dẫn ảnh (thay bằng ảnh thật)
    image_path = "data/sample/label_sample.jpg"
    
    # Kiểm tra file có tồn tại không
    if not Path(image_path).exists():
        print(f"⚠️ File không tồn tại: {image_path}")
        print("💡 Đặt ảnh nhãn bưu kiện vào thư mục data/sample/")
        return
    
    print(f"📸 Đang xử lý ảnh: {image_path}\n")
    
    # Bước 1: Tiền xử lý ảnh
    print("🔄 Bước 1: Tiền xử lý ảnh...")
    processed_image = processor.preprocess_image(image_path)
    processed_path = "data/output/processed.jpg"
    processor.save_processed_image(processed_image, processed_path)
    print(f"✅ Đã lưu ảnh xử lý tại: {processed_path}\n")
    
    # Bước 2: OCR - Nhận dạng text
    print("📝 Bước 2: Nhận dạng text...")
    ocr_result = ocr.extract_text_with_confidence(processed_path)
    print(f"Text nhận dạng:\n{ocr_result['text']}")
    print(f"Độ tin cậy: {ocr_result['confidence']:.2f}%\n")
    
    # Bước 3: Phân loại khu vực
    print("🗺️ Bước 3: Phân loại khu vực...")
    classification = classifier.classify(ocr_result['text'])
    print(f"Khu vực: {classification['region_name']}")
    print(f"Tỉnh/Thành: {classification.get('province', 'N/A')}")
    print(f"Độ tin cậy: {classification['confidence'] * 100:.1f}%\n")


def example_structured_data():
    """Ví dụ trích xuất dữ liệu có cấu trúc"""
    print("=" * 50)
    print("VÍ DỤ 2: Trích xuất dữ liệu có cấu trúc")
    print("=" * 50)
    
    ocr = OCREngine()
    image_path = "data/sample/label_sample.jpg"
    
    if not Path(image_path).exists():
        print(f"⚠️ File không tồn tại: {image_path}")
        return
    
    # Trích xuất dữ liệu có cấu trúc
    print("📋 Đang trích xuất thông tin...")
    structured_data = ocr.extract_structured_data(image_path)
    
    print("\n📞 Thông tin liên hệ:")
    print(f"  - Số điện thoại: {structured_data['phone']}")
    
    print("\n📍 Địa chỉ:")
    print(f"  - Địa chỉ: {structured_data['address']}")
    print(f"  - Mã bưu chính: {structured_data['postal_code']}")
    
    print(f"\n📊 Độ tin cậy: {structured_data['confidence']:.2f}%\n")


def example_region_info():
    """Ví dụ lấy thông tin khu vực"""
    print("=" * 50)
    print("VÍ DỤ 3: Thông tin các khu vực")
    print("=" * 50)
    
    classifier = RegionClassifier()
    
    # Lấy danh sách tất cả khu vực
    print("\n📍 Danh sách các khu vực:\n")
    regions = classifier.get_all_regions()
    
    for region in regions:
        print(f"🌏 {region['name']} ({region['code']})")
        print(f"   Số lượng tỉnh/thành: {region['province_count']}")
        
        # Lấy danh sách tỉnh
        provinces = classifier.get_provinces_by_region(region['key'])
        print(f"   Các tỉnh/thành: {', '.join(provinces[:5])}...")
        print()


def example_test_classification():
    """Ví dụ test phân loại với các địa chỉ mẫu"""
    print("=" * 50)
    print("VÍ DỤ 4: Test phân loại với địa chỉ mẫu")
    print("=" * 50)
    
    classifier = RegionClassifier()
    
    # Danh sách địa chỉ test
    test_addresses = [
        "Số 1 Đại Cồ Việt, Hai Bà Trưng, Hà Nội",
        "123 Nguyễn Huệ, Quận 1, TP. Hồ Chí Minh",
        "456 Trần Phú, Hải Châu, Đà Nẵng",
        "789 Lê Duẩn, Thành phố Huế, Thừa Thiên Huế",
        "321 Hai Bà Trưng, Thành phố Cần Thơ",
        "Số 555 Trường Chinh, Ba Đình, Hà Nội",
        "777 Điện Biên Phủ, Quận 3, Sài Gòn"
    ]
    
    print("\n🧪 Đang test phân loại...\n")
    
    for i, address in enumerate(test_addresses, 1):
        result = classifier.classify(address)
        
        status = "✅" if result['region'] != 'unknown' else "❌"
        
        print(f"{status} Test {i}:")
        print(f"   Địa chỉ: {address}")
        print(f"   Khu vực: {result['region_name']}")
        print(f"   Độ tin cậy: {result['confidence'] * 100:.1f}%")
        
        if result['matched_keywords']:
            print(f"   Từ khóa khớp: {', '.join(result['matched_keywords'])}")
        
        print()


def example_image_processing():
    """Ví dụ các phương pháp xử lý ảnh"""
    print("=" * 50)
    print("VÍ DỤ 5: Các phương pháp xử lý ảnh")
    print("=" * 50)
    
    processor = ImageProcessor()
    image_path = "data/sample/label_sample.jpg"
    
    if not Path(image_path).exists():
        print(f"⚠️ File không tồn tại: {image_path}")
        print("💡 Đặt ảnh vào thư mục data/sample/")
        return
    
    print("\n🖼️ Đang thử các phương pháp xử lý...\n")
    
    # Danh sách các phương pháp
    methods = ['auto', 'grayscale', 'threshold', 'denoise']
    
    for method in methods:
        print(f"📌 Phương pháp: {method}")
        output_path = f"data/output/processed_{method}.jpg"
        
        try:
            processed = processor.preprocess_image(image_path, method=method)
            processor.save_processed_image(processed, output_path)
            print(f"   ✅ Đã lưu: {output_path}\n")
        except Exception as e:
            print(f"   ❌ Lỗi: {e}\n")


def main():
    """Hàm main chạy tất cả ví dụ"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "ỨNG DỤNG OCR NHẬN DẠNG NHÃN BƯU KIỆN" + " " * 12 + "║")
    print("║" + " " * 20 + "CÁC VÍ DỤ SỬ DỤNG" + " " * 21 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")
    
    try:
        # Chạy ví dụ 3: Thông tin khu vực (không cần ảnh)
        example_region_info()
        input("Nhấn Enter để tiếp tục...")
        
        # Chạy ví dụ 4: Test phân loại (không cần ảnh)
        example_test_classification()
        input("Nhấn Enter để tiếp tục...")
        
        # Các ví dụ cần ảnh
        print("\n💡 Lưu ý: Các ví dụ tiếp theo cần ảnh nhãn bưu kiện")
        print("   Đặt ảnh vào: data/sample/label_sample.jpg\n")
        
        choice = input("Có muốn chạy các ví dụ cần ảnh? (y/n): ").lower()
        
        if choice == 'y':
            # Ví dụ 1: Sử dụng cơ bản
            example_basic_usage()
            input("Nhấn Enter để tiếp tục...")
            
            # Ví dụ 2: Trích xuất dữ liệu
            example_structured_data()
            input("Nhấn Enter để tiếp tục...")
            
            # Ví dụ 5: Xử lý ảnh
            example_image_processing()
        
        print("\n✅ Hoàn thành tất cả ví dụ!")
        print("\n📚 Để chạy ứng dụng web, sử dụng lệnh:")
        print("   streamlit run app.py\n")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Đã dừng chương trình!")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")


if __name__ == "__main__":
    main()
