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
        Schema::create('tbl_contact', function (Blueprint $table) {
            $table->bigIncrements('contactId');
            $table->string('fullName');
            $table->string('phoneNumber')->nullable();
            $table->string('email')->nullable();
            $table->text('message');
            $table->string('isReply', 2)->default('n'); // 'n': chưa trả lời, 'y': đã trả lời
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
        Schema::dropIfExists('tbl_contact');
    }
};
