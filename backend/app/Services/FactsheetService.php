<?php

namespace App\Services;

use App\Models\Animal;

class FactsheetService
{
    public function findByClassId(int $classId): ?Animal
    {
        return Animal::where('class_id', $classId)->first();
    }

    public function format(Animal $animal): array
    {
        return [
            'id' => $animal->id,
            'common_name' => $animal->common_name,
            'scientific_name' => $animal->scientific_name,
            'habitat' => $animal->habitat,
            'diet' => $animal->diet,
            'iucn_status' => $animal->iucn_status,
        ];
    }
}