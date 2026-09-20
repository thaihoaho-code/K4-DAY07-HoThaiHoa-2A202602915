from dotenv import load_dotenv
load_dotenv()
from embeddings import GeminiEmbedder
from chunking import compute_similarity

pairs=[('Shopee cho phép người mua gửi yêu cầu trả hàng/hoàn tiền trong các trường hợp đủ điều kiện.','Chính sách trả hàng và hoàn tiền quy định các trường hợp người mua có thể yêu cầu hoàn trả sản phẩm.'),('Sản phẩm hạn chế trả hàng chỉ được hoàn trả trong một số trường hợp nhất định.','Shopee hướng dẫn cách đóng gói đơn hàng trước khi giao cho đơn vị vận chuyển.'),('Người mua có thể trả hàng vì đổi ý hoặc không còn nhu cầu nếu đáp ứng điều kiện của Shopee.','Một số sản phẩm được phép hoàn trả khi người mua thay đổi nhu cầu mua hàng.'),('Chính sách bảo hành quy định việc hỗ trợ sản phẩm mua tại Shopee.','Người mua có thể theo dõi tình trạng vận chuyển của đơn hàng hoàn trả.'),('Shopee có các phương thức gửi hàng hoàn trả và quy định về phí hoàn trả.','Khi trả hàng, người mua cần chọn phương thức vận chuyển và kiểm tra chi phí gửi hàng hoàn.')]; embedder=GeminiEmbedder(); [print(f'{i}: {round(compute_similarity(embedder(a), embedder(b)), 6)}') for i,(a,b) in enumerate(pairs,1)]
