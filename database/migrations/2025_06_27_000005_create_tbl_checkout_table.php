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
        Schema::create('tbl_checkout', function (Blueprint $table) {
            $table->bigIncrements('checkoutId');
            $table->unsignedBigInteger('bookingId');
            $table->decimal('amount', 15, 2)->default(0);
            $table->string('paymentStatus', 2)->default('n'); // 'y': đã thanh toán, 'n': chưa thanh toán
            $table->string('paymentMethod', 50)->nullable();
            $table->timestamp('paymentDate')->useCurrent();
            $table->string('transactionId')->nullable();
            $table->timestamps();

            $table->foreign('bookingId')->references('bookingId')->on('tbl_booking')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('tbl_checkout');
    }
};
