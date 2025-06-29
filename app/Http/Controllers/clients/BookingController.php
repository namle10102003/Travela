<?php

namespace App\Http\Controllers\clients;

use App\Http\Controllers\Controller;
use App\Models\clients\Booking;
use App\Models\clients\Checkout;
use App\Models\clients\Tours;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class BookingController extends Controller
{
    private $tour;
    private $booking;
    private $checkout;

    public function __construct()
    {
        parent::__construct(); // Gọi constructor của Controller để khởi tạo $user
        $this->tour = new Tours();
        $this->booking = new Booking();
        $this->checkout = new Checkout();
    }

    public function index($id)
    {
        $title = 'Đặt Tour';
        $tour = $this->tour->getTourDetail($id);
        
        return view('clients.booking', compact('title', 'tour'));
    }

    public function createBooking(Request $req)
    {
        // dd($req);
        $address = $req->input('address');
        $email = $req->input('email');
        $fullName = $req->input('fullName');
        $numAdults = $req->input('numAdults');
        $numChildren = $req->input('numChildren');
        $paymentMethod = $req->input('payment_hidden');
        $tel = $req->input('tel');
        $totalPrice = $req->input('totalPrice');
        $tourId = $req->input('tourId');
        $userId = $this->getUserId();
        /**
         * Xử lý booking và checkout
         */
        $dataBooking = [
            'tourId' => $tourId,
            'userId' => $userId,
            'address' => $address,
            'fullName' => $fullName,
            'email' => $email,
            'numAdults' => $numAdults,
            'numChildren' => $numChildren,
            'phoneNumber' => $tel,
            'totalPrice' => $totalPrice,
            'created_at' => now(),
            'updated_at' => now()
        ];

        $bookingId = $this->booking->createBooking($dataBooking);

        $dataCheckout = [
            'bookingId' => $bookingId,
            'paymentMethod' => $paymentMethod,
            'amount' => $totalPrice,
            'paymentStatus' => ($paymentMethod === 'paypal-payment' || $paymentMethod === 'momo-payment') ? 'y' : 'n',
            'created_at' => now(),
            'updated_at' => now()
        ];

        if ($paymentMethod === 'paypal-payment') {
            $dataCheckout['transactionId'] = $req->transactionIdPaypal;
        } elseif ($paymentMethod === 'momo-payment') {
            $dataCheckout['transactionId'] = $req->transactionIdMomo;
        }
        $checkoutId = $this->checkout->createCheckout($dataCheckout);

        if (empty($bookingId) && !$checkoutId) {
            toastr()->error('Có vấn đề khi đặt tour!');
            return redirect()->back(); // Quay lại trang hiện tại nếu có lỗi
        }

        /**
         * Update quantity mới cho tour đó, trừ số lượng
         */
        $tour = $this->tour->getTourDetail($tourId);
        $dataUpdate = [
            'quantity' => $tour->quantity - ($numAdults + $numChildren)
        ];

        $updateQuantity = $this->tour->updateTours($tourId, $dataUpdate);

        /******************************* */

        toastr()->success('Đặt tour thành công!');
        return redirect()->route('tour-booked', [
            'bookingId' => $bookingId,
            'checkoutId' => $checkoutId,
        ]);

    }

    public function createMomoPayment(Request $request)
    {
        // Lưu thông tin booking vào session
        $bookingData = [
            'address' => $request->input('address'),
            'email' => $request->input('email'),
            'fullName' => $request->input('fullName'),
            'numAdults' => $request->input('numAdults'),
            'numChildren' => $request->input('numChildren'),
            'tel' => $request->input('tel'),
            'totalPrice' => $request->input('totalPrice')
        ];
        
        session()->put('tourId', $request->tourId);
        session()->put('bookingData', $bookingData);
        
        // Đảm bảo session được lưu trước khi tiếp tục
        session()->save();
        
        // Thêm một delay nhỏ để đảm bảo session được ghi hoàn toàn
        usleep(100000); // 0.1 giây
        
        // Kiểm tra xem session đã được lưu chưa
        if (!session()->has('tourId') || !session()->has('bookingData')) {
            return response()->json(['error' => 'Lỗi lưu thông tin đặt tour. Vui lòng thử lại!'], 500);
        }
        
        try {
            // $amount = $request->amount;
            $amount = 10000;
    
            // Các thông tin cần thiết của MoMo
            $endpoint = "https://test-payment.momo.vn/v2/gateway/api/create";
            $partnerCode = "MOMOBKUN20180529"; // mã partner của bạn
            $accessKey = "klm05TvNBzhg7h7j"; // access key của bạn
            $secretKey = "at67qH6mk8w5Y1nAyMoYKMWACiEi2bsa"; // secret key của bạn
    
            $orderInfo = "Thanh toán đơn hàng";
            $requestId = time();
            $orderId = time();
            $extraData = "";
            $redirectUrl = route('momo.callback'); 
            $ipnUrl = route('momo.callback'); // URL IPN
            $requestType = 'captureWallet'; // Kiểu yêu cầu
    
            // Tạo rawHash và chữ ký theo cách thủ công
            $rawHash = "accessKey=" . $accessKey . 
                       "&amount=" . $amount . 
                       "&extraData=" . $extraData . 
                       "&ipnUrl=" . $ipnUrl . 
                       "&orderId=" . $orderId . 
                       "&orderInfo=" . $orderInfo . 
                       "&partnerCode=" . $partnerCode . 
                       "&redirectUrl=" . $redirectUrl . 
                       "&requestId=" . $requestId . 
                       "&requestType=" . $requestType;
    
            // Tạo chữ ký
            $signature = hash_hmac("sha256", $rawHash, $secretKey);
    
            // Dữ liệu gửi đến MoMo
            $data = [
                'partnerCode' => $partnerCode,
                'partnerName' => "Test", // Tên đối tác
                'storeId' => "MomoTestStore", // ID cửa hàng
                'requestId' => $requestId,
                'amount' => $amount,
                'orderId' => $orderId,
                'orderInfo' => $orderInfo,
                'redirectUrl' => $redirectUrl,
                'ipnUrl' => $ipnUrl,
                'lang' => 'vi',
                'extraData' => $extraData,
                'requestType' => $requestType,
                'signature' => $signature
            ];
    
            // Gửi yêu cầu POST đến MoMo để tạo yêu cầu thanh toán
            $response = Http::post($endpoint, $data);
    
            if ($response->successful()) {
                $body = $response->json();
                if (isset($body['payUrl'])) {
                    return response()->json(['payUrl' => $body['payUrl']]);
                } else {
                    // Trả về thông tin lỗi trong response nếu không có 'payUrl'
                    return response()->json(['error' => 'Invalid response from MoMo', 'details' => $body], 400);
                }
            } else {
                // Trả về thông tin lỗi trong response nếu lỗi kết nối
                return response()->json(['error' => 'Lỗi kết nối với MoMo', 'details' => $response->body()], 500);
            }
        } catch (\Exception $e) {
            // Trả về chi tiết ngoại lệ trong response
            return response()->json(['error' => 'Đã xảy ra lỗi', 'message' => $e->getMessage(), 'trace' => $e->getTraceAsString()], 500);
        }
    }
    

    public function handlePaymentMomoCallback(Request $request)
    {
        $resultCode = $request->input('resultCode');
        $transId = $request->input('transId');
        // dd(session()->get('tourId'));
        $tourId = session()->get('tourId'); 

        if (!$tourId) {
            // Nếu không có tourId trong session, redirect về trang chủ
            toastr()->error('Phiên thanh toán đã hết hạn!');
            return redirect()->route('home');
        }

        $tour = $this->tour->getTourDetail($tourId);

        if (!$tour) {
            // Nếu không tìm thấy tour, redirect về trang chủ
            toastr()->error('Không tìm thấy thông tin tour!');
            return redirect()->route('home');
        }

        // Lấy thông tin booking từ session
        $bookingData = session()->get('bookingData');
        
        if ($resultCode == '0') {
            // Thanh toán thành công - Tạo booking và checkout
            if ($bookingData) {
                $userId = $this->getUserId();
                
                // Tạo booking
                $dataBooking = [
                    'tourId' => $tourId,
                    'userId' => $userId,
                    'address' => $bookingData['address'],
                    'fullName' => $bookingData['fullName'],
                    'email' => $bookingData['email'],
                    'numAdults' => $bookingData['numAdults'],
                    'numChildren' => $bookingData['numChildren'],
                    'phoneNumber' => $bookingData['tel'],
                    'totalPrice' => $bookingData['totalPrice'],
                    'created_at' => now(),
                    'updated_at' => now()
                ];

                $bookingId = $this->booking->createBooking($dataBooking);

                // Tạo checkout
                $dataCheckout = [
                    'bookingId' => $bookingId,
                    'paymentMethod' => 'momo-payment',
                    'amount' => $bookingData['totalPrice'],
                    'paymentStatus' => 'y',
                    'transactionId' => $transId,
                    'created_at' => now(),
                    'updated_at' => now()
                ];

                $checkoutId = $this->checkout->createCheckout($dataCheckout);

                // Cập nhật số lượng tour
                $dataUpdate = [
                    'quantity' => $tour->quantity - ($bookingData['numAdults'] + $bookingData['numChildren'])
                ];
                $this->tour->updateTours($tourId, $dataUpdate);

                // Xóa session data
                session()->forget(['tourId', 'bookingData']);
                
                toastr()->success('Thanh toán MoMo thành công! Tour đã được đặt.');
                return redirect()->route('tour-booked', [
                    'bookingId' => $bookingId,
                    'checkoutId' => $checkoutId,
                ]);
            } else {
                // Không có dữ liệu booking trong session
                session()->forget('tourId');
                toastr()->error('Không tìm thấy thông tin đặt tour!');
                return redirect()->route('tour-detail', ['id' => $tourId]);
            }
        } else {
            // Thanh toán thất bại
            session()->forget(['tourId', 'bookingData']);
            toastr()->error('Thanh toán MoMo thất bại! Vui lòng thử lại.');
            return redirect()->route('tour-detail', ['id' => $tourId]);
        }
    }

    //Kiểm tra người dùng đã đặt và hoàn thành tour hay chưa để đánh giá
    public function checkBooking(Request $req){
        $tourId = $req->tourId;
        $userId = $this->getUserId();
        $check = $this->booking->checkBooking($tourId,$userId);
        if (!$check) {
            return response()->json(['success' => false]);
        }
        return response()->json(['success' => true]);
    }

}
