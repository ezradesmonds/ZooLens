<?php

namespace App\Services;

use App\Models\Animal;
use App\Models\Detection;
use App\Models\User;

class CollectionService
{
    /**
     * Simpan hasil deteksi ke riwayat. Kalau confidence cukup dan satwa belum
     * ada di koleksi user, masukkan ke koleksi dan kembalikan info badge.
     */
    public function record(User $user, Animal $animal, array $detection, int $imageWidth, int $imageHeight): array
    {
        [$x1, $y1, $x2, $y2] = array_map(fn ($v) => max(0, (int) round($v)), $detection['bbox']);

        Detection::create([
            'user_id' => $user->id,
            'animal_id' => $animal->id,
            'confidence' => $detection['confidence'],
            'bbox_x1' => $x1,
            'bbox_y1' => $y1,
            'bbox_x2' => $x2,
            'bbox_y2' => $y2,
            'image_width' => $imageWidth,
            'image_height' => $imageHeight,
        ]);

        $isNew = false;

        if ($detection['confidence'] >= config('zoolens.confidence_threshold')) {
            $alreadyCollected = $user->animals()->where('animals.id', $animal->id)->exists();

            if (! $alreadyCollected) {
                $user->animals()->attach($animal->id, ['discovered_at' => now()]);
                $isNew = true;
            }
        }

        $badge = $isNew ? $animal->badge : null;

        return [
            'is_new_discovery' => $isNew,
            'badge' => $badge ? ['name' => $badge->name, 'icon' => $badge->icon] : null,
        ];
    }

    public function progress(User $user): array
    {
        $total = Animal::count();
        $collected = $user->animals()->count();

        return [
            'collected' => $collected,
            'total' => $total,
            'percentage' => $total > 0 ? (int) round($collected / $total * 100) : 0,
        ];
    }
}