<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\HasOne;

class Animal extends Model
{
    protected $fillable = [
        'class_id',
        'common_name',
        'scientific_name',
        'habitat',
        'diet',
        'iucn_status',
    ];

    public function badge(): HasOne
    {
        return $this->hasOne(Badge::class);
    }

    public function detections(): HasMany
    {
        return $this->hasMany(Detection::class);
    }

    public function users(): BelongsToMany
    {
        return $this->belongsToMany(User::class, 'user_animals')
            ->withPivot('discovered_at')
            ->withTimestamps();
    }
}