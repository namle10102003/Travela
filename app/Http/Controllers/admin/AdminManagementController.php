<?php

namespace App\Http\Controllers\admin;

use App\Http\Controllers\Controller;
use App\Models\admin\AdminModel;
use Illuminate\Http\Request;

class AdminManagementController extends Controller
{
    private $admin;

    public function __construct()
    {
        $this->admin = new AdminModel();
    }
    public function index()
    {
        $title = 'Quản lý Admin';

        $admin = $this->admin->getAdmin();

        return view('admin.profile-admin', compact('title', 'admin'));
    }

    public function updateAdmin(Request $request)
    {
        $fullName = $request->fullName;
        $password = $request->password;
        $email = $request->email;
        $address = $request->address;

        $username = $request->session()->get('admin');
        $admin = $this->admin->getAdmin($username);
        $oldPass = $admin->password;

        if ($password != $oldPass) {
            $password = md5($password);
        }

        $dataUpdate = [
            'fullName' => $fullName,
            'password' => $password,
            'email' => $email,
            'address' => $address
        ];
        $update = $this->admin->updateAdmin($username, $dataUpdate);
        $newinfo = $this->admin->getAdmin($username);
        // Cập nhật lại tên mới vào session để hiển thị đúng ngoài dashboard
        $request->session()->put('admin_fullname', $newinfo->fullName);
        return response()->json([
            'success' => true,
            'data' => $newinfo
        ]);
    }

    public function updateAvatar(Request $req)
    {
        // dd($req->all());
        $avatar = $req->file('avatarAdmin');

        // Tạo tên mới cho tệp ảnh
        $filename = 'avt_admin.jpg'; // Tên tệp mới
        unlink(public_path('admin/assets/images/user-profile/avt_admin.jpg'));

        // Di chuyển ảnh vào thư mục public/admin/assets/images/user-profile/
        $update = $avatar->move(public_path('admin/assets/images/user-profile'), $filename);

        if (!$update) {
            return response()->json(['error' => true, 'message' => 'Có vấn đề khi cập nhật ảnh!']);
        }
        return response()->json(['success' => true, 'message' => 'Cập nhật ảnh thành công!']);
    }

}
