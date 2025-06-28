<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('tbl_booking', function (Blueprint $table) {
            $table->bigIncrements('bookingId');
            $table->unsignedBigInteger('tourId');
            $table->unsignedBigInteger('userId');
            $table->timestamp('bookingDate')->useCurrent();
            $table->integer('numAdults')->nullable();
            $table->integer('numChildren')->nullable();
            $table->decimal('totalPrice', 12, 2)->nullable();
            $table->string('bookingStatus', 2)->default('b'); // b: booked, f: finished, c: canceled
            $table->string('address')->nullable();
            $table->string('email')->nullable();
            $table->string('fullName')->nullable();
            $table->string('phoneNumber')->nullable();
            $table->timestamps();

            $table->foreign('tourId')->references('tourId')->on('tbl_tours')->onDelete('cascade');
            // $table->foreign('userId')->references('userId')->on('tbl_users')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('tbl_booking');
    }
};
