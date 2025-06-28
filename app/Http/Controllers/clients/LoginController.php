<?php

namespace App\Http\Controllers\clients;

use Illuminate\Support\Str;
use App\Http\Controllers\Controller;
use App\Models\clients\Login;
use App\Models\clients\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\DB;

class LoginController extends Controller
{

    private $login;
    protected $user;

    public function __construct()
    {
        $this->login = new Login();
        $this->user = new User();
    }
    public function index()
    {
        $title = 'Đăng nhập';
        return view('clients.login', compact('title'));
    }


    public function register(Request $request)
{
    DB::beginTransaction(); // Thêm dòng này

    $username_regis = $request->username_regis;
    $email = $request->email;
    $password_regis = $request->password_regis;

    $checkAccountExist = $this->login->checkUserExist($username_regis, $email);
    if ($checkAccountExist) {
        return response()->json([
            'success' => false,
            'message' => 'Tên người dùng hoặc email đã tồn tại!'
        ]);
    }

    $activation_token = Str::random(60);

    $dataInsert = [
        'username'         => $username_regis,
        'email'            => $email,
        'password'         => md5($password_regis),
        'activation_token' => $activation_token,
        'isActive'         => 'n'
    ];

    try {
        $this->login->registerAcount($dataInsert);
        $this->sendActivationEmail($email, $activation_token);

        DB::commit(); // Thêm dòng này nếu thành công

        return response()->json([
            'success' => true,
            'message' => 'Đăng ký thành công! Vui lòng kiểm tra email để kích hoạt tài khoản.'
        ]);
    } catch (\Exception $e) {
        DB::rollBack(); // Thêm dòng này để hủy dữ liệu đã insert nếu thất bại
        Log::error('Register error', ['error' => $e->getMessage()]);
        return response()->json([
            'success' => false,
            'message' => 'Có lỗi xảy ra khi đăng ký. Vui lòng thử lại!'
        ]);
    }
}

    public function sendActivationEmail($email, $token)
    {
        $activation_link = route('activate.account', ['token' => $token]);

        Mail::send('clients.mail.emails_activation', ['link' => $activation_link], function ($message) use ($email) {
            $message->to($email);
            $message->subject('Kích hoạt tài khoản của bạn');
        });
    }

    public function activateAccount($token)
    {
        $user = $this->login->getUserByToken($token);
        if ($user) {
            $this->login->activateUserAccount($token); // update isActive = 'y'
            return redirect('/login')->with('message', 'Tài khoản của bạn đã được kích hoạt!');
        } else {
            return redirect('/login')->with('error', 'Mã kích hoạt không hợp lệ!');
        }
    }

    //Xử lý người dùng đăng nhập
    public function login(Request $request)
    {
        $username = $request->username;
        $password = $request->password;

        $data_login = [
            'username' => $username,
            'password' => md5($password),
            'isActive' => 'y' // Chỉ cho phép đăng nhập khi đã kích hoạt
        ];

        Log::info('Login attempt', $data_login);

        $user_login = $this->login->login($data_login);
        Log::info('Login query result', ['user_login' => $user_login ? (is_object($user_login) && method_exists($user_login, 'toArray') ? $user_login->toArray() : $user_login) : null]);

        $userId = $this->user->getUserId($username);
        $user = $this->user->getUser($userId);

        if ($user_login != null) {
            $request->session()->put('username', $username);
            $request->session()->put('avatar', isset($user->avatar) ? $user->avatar : null);
            toastr()->success("Đăng nhập thành công!",'Thông báo');
            return response()->json([
                'success' => true,
                'message' => 'Đăng nhập thành công!',
                'redirectUrl' => route('home'),
            ]);
        } else {
            return response()->json([
                'success' => false,
                'message' => 'Thông tin tài khoản không chính xác hoặc tài khoản chưa được kích hoạt!',
            ]);
        }
    }

    //Xử lý đăng xuất
    public function logout(Request $request)
    {
        // Xóa session lưu trữ thông tin người dùng đã đăng nhập
        $request->session()->forget('username');
        $request->session()->forget('avatar');
        $request->session()->forget('userId');
        toastr()->success("Đăng xuất thành công!",'Thông báo');
        return redirect()->route('home');
    }


}
