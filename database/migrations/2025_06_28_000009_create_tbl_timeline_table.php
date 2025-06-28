<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('tbl_timeline', function (Blueprint $table) {
            $table->bigIncrements('timelineId');
            $table->unsignedBigInteger('tourId');
            $table->string('title');
            $table->text('description')->nullable();
            $table->timestamps();

            // $table->foreign('tourId')->references('tourId')->on('tbl_tours')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('tbl_timeline');
    }
};
