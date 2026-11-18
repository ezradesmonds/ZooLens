<?php

namespace Tests\Feature;

use App\Services\FactsheetService;
use Database\Seeders\AnimalSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class AnimalMappingTest extends TestCase
{
    use RefreshDatabase;

    public function test_every_model_class_maps_to_a_complete_animal(): void
    {
        $this->seed(AnimalSeeder::class);

        $expected = [
            0 => 'Elephant',
            1 => 'Giraffe',
            2 => 'Zebra',
            3 => 'Tiger',
            4 => 'Rhinoceros',
        ];

        foreach ($expected as $classId => $name) {
            $animal = app(FactsheetService::class)->findByClassId($classId);

            $this->assertNotNull($animal, "class_id {$classId} tidak punya satwa");
            $this->assertSame($name, $animal->common_name);
            $this->assertNotNull($animal->badge, "{$name} tidak punya badge");
            $this->assertSame(strtolower($name), $animal->badge->icon, "{$name} icon badge tidak sesuai kunci");

            foreach (['scientific_name', 'habitat', 'diet', 'iucn_status'] as $field) {
                $this->assertNotContains($animal->{$field}, ['TODO', '--', ''], "{$name}.{$field} belum diisi");
            }

            $this->assertArrayHasKey(
                strtolower($name),
                config('zoolens.names_id'),
                "{$name} belum ada di config zoolens.names_id"
            );
        }
    }
}