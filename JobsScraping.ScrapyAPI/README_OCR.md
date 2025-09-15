# OCR Integration với FastAPI

## Tổng quan
Tích hợp OCR (Optical Character Recognition) vào API CV để tự động xử lý file ảnh và PDF khi upload CV.

## Tính năng
- Upload file CV (PNG, JPG, JPEG, PDF) với OCR tự động
- Upload CV từ URL với OCR tự động
- Chỉ xử lý OCR mà không lưu CV
- Lưu trữ kết quả OCR vào database

## Cài đặt

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Cấu hình biến môi trường
Tạo file `.env` với các biến sau:
```env
# Database Configuration
DATABASE_URL=your_database_connection_string_here

# OCR API Configuration
OCR_API_KEY=your_optiic_api_key_here
OCR_API_URL=https://api.optiic.dev/process

# FastAPI Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### 3. Cập nhật database schema
Chạy migration để thêm các trường mới cho OCR:
```sql
ALTER TABLE CVs ADD COLUMN OCRText TEXT;
ALTER TABLE CVs ADD COLUMN CVSource VARCHAR(50);
ALTER TABLE CVs ADD COLUMN OriginalFilename VARCHAR(255);
ALTER TABLE CVs ADD COLUMN CVUrl VARCHAR(500);
ALTER TABLE CVs ADD COLUMN CreatedDate DATETIME DEFAULT GETUTCDATE();
```

## Sử dụng API

### 1. Upload CV với OCR
```bash
# Upload file
curl -X POST "http://localhost:8000/cvs/upload-with-ocr" \
  -F "user_id=1" \
  -F "name=John Doe" \
  -F "cv_file=@/path/to/cv.pdf"

# Upload từ URL
curl -X POST "http://localhost:8000/cvs/upload-with-ocr" \
  -F "user_id=1" \
  -F "cv_url=https://example.com/cv.png"
```

### 2. Chỉ xử lý OCR
```bash
# OCR file
curl -X POST "http://localhost:8000/cvs/ocr-only" \
  -F "cv_file=@/path/to/image.png"

# OCR URL
curl -X POST "http://localhost:8000/cvs/ocr-only" \
  -F "cv_url=https://example.com/image.png"
```

### 3. Lấy CV với thông tin OCR
```bash
# Lấy CV theo ID
GET /cvs/{cv_id}

# Lấy CV theo user ID
GET /cvs/user/{user_id}

# Lấy thống kê CV
GET /cvs/stats/summary
```

## Cấu trúc Response

### CV Response với OCR
```json
{
  "id": 1,
  "user_id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone_number": "+1234567890",
  "address": "123 Main St",
  "summary": "Experienced developer",
  "ocr_text": "Extracted text from CV...",
  "cv_source": "file",
  "original_filename": "cv.pdf",
  "cv_url": null,
  "created_date": "2024-01-01T00:00:00"
}
```

### OCR Response
```json
{
  "ocr_text": "Extracted text from image...",
  "processed_at": "2024-01-01T00:00:00",
  "source": "file"
}
```

## Xử lý lỗi

### File không được hỗ trợ
```json
{
  "detail": "File type not supported. Only PNG, JPG, JPEG, PDF files are allowed."
}
```

### OCR thất bại
```json
{
  "detail": "OCR processing failed"
}
```

### User không tồn tại
```json
{
  "detail": "User not found"
}
```

## Lưu ý
- Đảm bảo có API key hợp lệ từ Optiic
- File upload giới hạn kích thước (có thể cấu hình trong FastAPI)
- Kết quả OCR được lưu vào database để sử dụng sau này
- Hỗ trợ cả file upload và URL processing
