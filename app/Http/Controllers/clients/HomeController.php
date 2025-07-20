<?php

namespace App\Http\Controllers\clients;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\clients\Home;
use App\Models\clients\Tours;
use Illuminate\Support\Facades\Http;

use function PHPUnit\Framework\isEmpty;

class HomeController extends Controller
{
    private $homeTours;
    private $tours;

    public function __construct()
    {
        parent::__construct();
        $this->homeTours = new Home();
        $this->tours = new Tours();
    }
    public function index()
    {
        $title = 'Trang chủ';
        $tours = $this->homeTours->getHomeTours();

        $userId = $this->getUserId();
        $toursPopular = $this->tours->toursPopular(6);

        // dd($toursPopular);
        return view('clients.home', compact('title', 'tours', 'toursPopular'));
    }


}
