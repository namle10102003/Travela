<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('tbl_users', function (Blueprint $table) {
            $table->bigIncrements('userId');
            $table->string('username')->unique();
            $table->string('email')->unique();
            $table->string('password');
            $table->string('activation_token', 100)->nullable();
            $table->string('isActive', 2)->default('n'); // 'y': đã kích hoạt, 'n': chưa kích hoạt
            $table->string('avatar')->nullable(); // Thêm trường avatar cho user
            $table->string('fullName')->nullable();
            $table->string('phoneNumber')->nullable();
            $table->string('address')->nullable();
            $table->string('ipAddress')->nullable();
            $table->string('status', 1)->nullable()->comment('b: block, d: delete');
            $table->dateTime('createdDate')->nullable();
            $table->dateTime('updatedDate')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('tbl_users');
    }
};