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
        Schema::create('tbl_tours', function (Blueprint $table) {
            $table->bigIncrements('tourId');
            $table->string('title');
            $table->text('description')->nullable();
            $table->decimal('priceAdult', 10, 2)->nullable();
            $table->decimal('priceChild', 10, 2)->nullable();
            $table->string('time')->nullable();
            $table->string('destination')->nullable();
            $table->integer('quantity')->nullable();
            $table->string('domain')->nullable(); // Bắc - Trung - Nam
            $table->date('startDate')->nullable();
            $table->date('endDate')->nullable();
            $table->boolean('availability')->default(1);
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
        Schema::dropIfExists('tbl_tours');
    }
};
