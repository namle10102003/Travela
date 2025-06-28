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
        Schema::create('tbl_reviews', function (Blueprint $table) {
            $table->bigIncrements('reviewId');
            $table->unsignedBigInteger('tourId');
            $table->unsignedBigInteger('userId');
            $table->tinyInteger('rating');
            $table->text('content')->nullable();
            $table->timestamp('timestamp')->useCurrent();
            $table->timestamps();

            $table->foreign('tourId')->references('tourId')->on('tbl_tours')->onDelete('cascade');
            $table->foreign('userId')->references('userId')->on('tbl_users')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('tbl_reviews');
    }
};
