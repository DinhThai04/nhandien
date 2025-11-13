"""
Ứng dụng Streamlit - OCR Nhận dạng và Phân loại Nhãn Bưu kiện
"""
import streamlit as st
from PIL import Image
import sys
from pathlib import Path
import os

# Thêm thư mục src vào path
sys.path.append(str(Path(__file__).parent))

from src.ocr_engine import OCREngine
from src.region_classifier import RegionClassifier
from src.image_processor import ImageProcessor
from config.config import APP_TITLE, APP_ICON, OUTPUT_DIR


# Cấu hình trang
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)


# CSS tùy chỉnh
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E88E5;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FFF3E0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF9800;
        margin: 1rem 0;
    }
    .result-card {
        background-color: #FAFAFA;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# Khởi tạo session state
if 'ocr_result' not in st.session_state:
    st.session_state.ocr_result = None
if 'classification_result' not in st.session_state:
    st.session_state.classification_result = None


@st.cache_resource
def load_engines():
    """Load các engine (cache để tăng hiệu suất)"""
    try:
        ocr = OCREngine()
        classifier = RegionClassifier()
        processor = ImageProcessor()
        return ocr, classifier, processor
    except Exception as e:
        st.error(f"⚠️ Lỗi khi khởi tạo engines: {e}")
        return None, None, None


def process_image(image, ocr_engine, classifier, processor):
    """Xử lý ảnh và trả về kết quả"""
    try:
        # Lưu ảnh tạm
        temp_path = OUTPUT_DIR / "temp_image.jpg"
        image.save(temp_path)
        
        # Tiền xử lý ảnh
        with st.spinner("🔄 Đang xử lý ảnh..."):
            processed = processor.preprocess_image(str(temp_path))
            processed_path = OUTPUT_DIR / "processed_image.jpg"
            processor.save_processed_image(processed, str(processed_path))
        
        # OCR
        with st.spinner("📝 Đang nhận dạng text..."):
            ocr_result = ocr_engine.extract_text_with_confidence(str(processed_path))
            structured_data = ocr_engine.extract_structured_data(str(processed_path))
        
        # Phân loại khu vực
        with st.spinner("🗺️ Đang phân loại khu vực..."):
            classification = classifier.classify(ocr_result['text'])
        
        return {
            'ocr': ocr_result,
            'structured': structured_data,
            'classification': classification,
            'processed_image': processed_path
        }
    
    except Exception as e:
        st.error(f"❌ Lỗi khi xử lý ảnh: {e}")
        return None


def main():
    """Hàm main của ứng dụng"""
    
    # Header
    st.markdown(f'<h1 class="main-header">{APP_ICON} {APP_TITLE}</h1>', 
                unsafe_allow_html=True)
    
    # Load engines
    ocr_engine, classifier, processor = load_engines()
    
    if not ocr_engine or not classifier or not processor:
        st.error("⚠️ Không thể khởi tạo ứng dụng. Vui lòng kiểm tra cài đặt Tesseract OCR.")
        st.info("""
        📋 **Hướng dẫn cài đặt Tesseract:**
        
        **Windows:**
        1. Download từ: https://github.com/UB-Mannheim/tesseract/wiki
        2. Cài đặt và thêm vào PATH
        3. Cập nhật đường dẫn trong `config/config.py`
        
        **Linux:**
        ```bash
        sudo apt-get install tesseract-ocr tesseract-ocr-vie
        ```
        """)
        return
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Cấu hình")
        
        # Thông tin khu vực
        st.subheader("📍 Khu vực giao hàng")
        regions = classifier.get_all_regions()
        for region in regions:
            st.info(f"**{region['name']}** ({region['code']}): {region['province_count']} tỉnh/thành")
        
        st.divider()
        
        # Hướng dẫn sử dụng
        st.subheader("📖 Hướng dẫn")
        st.markdown("""
        1. Upload ảnh nhãn bưu kiện
        2. Đợi hệ thống xử lý
        3. Xem kết quả nhận dạng và phân loại
        4. Download kết quả nếu cần
        """)
        
        st.divider()
        
        # Thông tin phiên bản
        st.caption("Version 1.0.0")
        st.caption("© 2024 OCR Postal Label System")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Ảnh Nhãn Bưu kiện")
        
        uploaded_file = st.file_uploader(
            "Chọn ảnh nhãn bưu kiện",
            type=['jpg', 'jpeg', 'png', 'bmp'],
            help="Hỗ trợ định dạng: JPG, JPEG, PNG, BMP"
        )
        
        if uploaded_file is not None:
            # Hiển thị ảnh gốc
            image = Image.open(uploaded_file)
            st.image(image, caption="Ảnh đã upload", use_column_width=True)
            
            # Nút xử lý
            if st.button("🚀 Bắt đầu xử lý", type="primary", use_container_width=True):
                result = process_image(image, ocr_engine, classifier, processor)
                
                if result:
                    st.session_state.ocr_result = result['ocr']
                    st.session_state.classification_result = result['classification']
                    st.session_state.structured_data = result['structured']
                    st.session_state.processed_image = result['processed_image']
                    st.success("✅ Xử lý thành công!")
    
    with col2:
        st.subheader("📊 Kết quả")
        
        if st.session_state.ocr_result:
            # Hiển thị kết quả phân loại
            classification = st.session_state.classification_result
            
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown("### 🗺️ Phân loại khu vực")
            
            if classification['region'] != 'unknown':
                st.markdown(f"""
                <div class="success-box">
                    <h3>✅ {classification['region_name']}</h3>
                    <p><strong>Độ tin cậy:</strong> {classification['confidence'] * 100:.1f}%</p>
                    {f"<p><strong>Tỉnh/Thành:</strong> {classification['province']}</p>" if classification['province'] else ""}
                    <p><strong>Từ khóa khớp:</strong> {', '.join(classification['matched_keywords'])}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="warning-box">
                    <p>⚠️ Không thể xác định khu vực. Vui lòng kiểm tra lại ảnh.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Thông tin chi tiết
            with st.expander("📝 Text nhận dạng được"):
                ocr_result = st.session_state.ocr_result
                st.text_area(
                    "Nội dung",
                    value=ocr_result['text'],
                    height=200,
                    disabled=True
                )
                st.metric("Độ tin cậy OCR", f"{ocr_result['confidence']:.1f}%")
            
            # Dữ liệu có cấu trúc
            with st.expander("📋 Thông tin trích xuất"):
                structured = st.session_state.structured_data
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.text_input("📞 Số điện thoại", structured['phone'], disabled=True)
                    st.text_input("📮 Mã bưu chính", structured['postal_code'], disabled=True)
                
                with col_b:
                    st.text_area("📍 Địa chỉ", structured['address'], height=100, disabled=True)
            
            # Ảnh đã xử lý
            if 'processed_image' in st.session_state:
                with st.expander("🖼️ Ảnh đã xử lý"):
                    processed_img = Image.open(st.session_state.processed_image)
                    st.image(processed_img, use_column_width=True)
            
            # Nút download
            st.divider()
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                # Download text
                text_data = f"""
=== KẾT QUẢ NHẬN DẠNG NHÃ BƯU KIỆN ===

KHU VỰC: {classification['region_name']}
Độ tin cậy: {classification['confidence'] * 100:.1f}%
Tỉnh/Thành: {classification.get('province', 'N/A')}

THÔNG TIN:
- Số điện thoại: {structured['phone']}
- Địa chỉ: {structured['address']}
- Mã bưu chính: {structured['postal_code']}

TEXT NHẬN DẠNG:
{ocr_result['text']}
"""
                st.download_button(
                    label="💾 Tải xuống kết quả (.txt)",
                    data=text_data,
                    file_name="ket_qua_ocr.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        else:
            st.info("👆 Vui lòng upload ảnh và nhấn 'Bắt đầu xử lý' để xem kết quả")


if __name__ == "__main__":
    main()
