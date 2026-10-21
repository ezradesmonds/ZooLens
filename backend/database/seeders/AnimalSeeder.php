<?php

namespace Database\Seeders;

use App\Models\Animal;
use Illuminate\Database\Seeder;

class AnimalSeeder extends Seeder
{
    public function run(): void
    {
        // TODO: urutan class_id sementara, ikut model Bryan (konfirmasi dulu).
        // TODO: scientific_name, habitat, diet, iucn_status isi dari IUCN Red List,
        //       lalu verifikasi manual. '--' pada iucn_status = belum diisi.
        $animals = [
            ['class_id' => 0, 'common_name' => 'Elephant',   'scientific_name' => 'TODO'],
            ['class_id' => 1, 'common_name' => 'Giraffe',    'scientific_name' => 'TODO'],
            ['class_id' => 2, 'common_name' => 'Zebra',      'scientific_name' => 'TODO'],
            ['class_id' => 3, 'common_name' => 'Tiger',      'scientific_name' => 'Panthera tigris'],
            ['class_id' => 4, 'common_name' => 'Rhinoceros', 'scientific_name' => 'TODO'],
        ];

        foreach ($animals as $data) {
            $animal = Animal::updateOrCreate(
                ['common_name' => $data['common_name']],
                [
                    'class_id' => $data['class_id'],
                    'scientific_name' => $data['scientific_name'],
                    'habitat' => 'TODO',
                    'diet' => 'TODO',
                    'iucn_status' => '--',
                ]
            );

            $animal->badge()->updateOrCreate(
                ['animal_id' => $animal->id],
                [
                    'name' => 'Lencana '.$animal->common_name,
                    'description' => 'Berhasil menemukan '.$animal->common_name.'.',
                    'icon' => 'TODO', // path ikon dari Ivy
                ]
            );
        }
    }
}