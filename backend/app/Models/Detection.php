<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Detection extends Model
{
    protected $fillable = [
        'user_id',
        'animal_id',
        'confidence',
        'bbox_x1',
        'bbox_y1',
        'bbox_x2',
        'bbox_y2',
        'image_width',
        'image_height',
    ];

    protected function casts(): array
    {
        return [
            'confidence' => 'float',
        ];
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function animal(): BelongsTo
    {
        return $this->belongsTo(Animal::class);
    }
}