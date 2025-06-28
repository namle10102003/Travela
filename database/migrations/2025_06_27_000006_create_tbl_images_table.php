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
        Schema::create('tbl_images', function (Blueprint $table) {
            $table->bigIncrements('imageId');
            $table->unsignedBigInteger('tourId');
            $table->string('imageURL');
            $table->text('description')->nullable();
            $table->dateTime('uploadDate')->nullable();
            $table->timestamps();

            // $table->foreign('tourId')->references('tourId')->on('tbl_tours')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('tbl_images');
    }
};
