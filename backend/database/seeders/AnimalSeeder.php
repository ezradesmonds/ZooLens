<?php

namespace Database\Seeders;

use App\Models\Animal;
use Illuminate\Database\Seeder;

class AnimalSeeder extends Seeder
{
    public function run(): void
    {
        $animals = [
            [
                'class_id' => 0,
                'common_name' => 'Elephant',
                'scientific_name' => 'Elephas maximus',
                'habitat' => 'Hutan tropis, hutan sekunder, dan padang rumput di Asia Selatan dan Tenggara.',
                'diet' => 'Herbivora: rumput, daun, ranting, kulit kayu, dan buah. Dapat makan hingga sekitar 150 kg per hari.',
                'iucn_status' => 'EN', 
            ],
            [
                'class_id' => 1,
                'common_name' => 'Giraffe',
                'scientific_name' => 'Giraffa camelopardalis',
                'habitat' => 'Sabana dan hutan terbuka di Afrika.',
                'diet' => 'Herbivora: daun akasia, tunas, dan buah. Lehernya yang panjang menjangkau dedaunan tinggi.',
                'iucn_status' => 'VU', 
            ],
            [
                'class_id' => 2,
                'common_name' => 'Zebra',
                'scientific_name' => 'Equus quagga',
                'habitat' => 'Padang rumput dan sabana di Afrika bagian timur dan selatan.',
                'diet' => 'Herbivora: terutama rumput, kadang daun dan semak.',
                'iucn_status' => 'NT', 
            ],
            [
                'class_id' => 3,
                'common_name' => 'Tiger',
                'scientific_name' => 'Panthera tigris',
                'habitat' => 'Hutan tropis, hutan bakau, dan padang rumput di Asia.',
                'diet' => 'Karnivora: rusa, babi hutan, dan mamalia besar lain.',
                'iucn_status' => 'EN', 
            ],
            [
                'class_id' => 4,
                'common_name' => 'Rhinoceros',
                'scientific_name' => 'Ceratotherium simum',
                'habitat' => 'Sabana dan padang rumput di Afrika bagian selatan dan timur.',
                'diet' => 'Herbivora: terutama rumput pendek.',
                'iucn_status' => 'NT', 
            ],
        ];

        foreach ($animals as $data) {
            $animal = Animal::updateOrCreate(
                ['common_name' => $data['common_name']],
                [
                    'class_id' => $data['class_id'],
                    'scientific_name' => $data['scientific_name'],
                    'habitat' => $data['habitat'],
                    'diet' => $data['diet'],
                    'iucn_status' => $data['iucn_status'],
                ]
            );

            $animal->badge()->updateOrCreate(
                ['animal_id' => $animal->id],
                [
                    'name' => 'Lencana '.$animal->common_name,
                    'description' => 'Berhasil menemukan '.$animal->common_name.'.',
                    'icon' => strtolower($animal->common_name), 
                ]
            );
        }
    }
}