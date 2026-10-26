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
        Schema::create('detections', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('animal_id')->constrained('animals');
            $table->decimal('confidence', 5, 4);
            $table->unsignedInteger('bbox_x1');
            $table->unsignedInteger('bbox_y1');
            $table->unsignedInteger('bbox_x2');
            $table->unsignedInteger('bbox_y2');
            $table->unsignedInteger('image_width');
            $table->unsignedInteger('image_height');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('detections');
    }
};
