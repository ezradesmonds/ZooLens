<?php

namespace Tests\Feature;

use App\Models\Animal;
use App\Models\User;
use App\Services\FactsheetService;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Http;
use Tests\TestCase;

class FactsheetTest extends TestCase
{
    use RefreshDatabase;

    private function makeTiger(): Animal
    {
        return Animal::create([
            'class_id' => 3,
            'common_name' => 'Tiger',
            'scientific_name' => 'Panthera tigris',
            'habitat' => 'test',
            'diet' => 'test',
            'iucn_status' => 'EN',
        ]);
    }

    private function fakeAi(int $classId): void
    {
        Http::fake(['*' => Http::response([
            'image_width' => 1280,
            'image_height' => 960,
            'detections' => [
                ['class_id' => $classId, 'confidence' => 0.91, 'bbox' => [100, 80, 300, 260]],
            ],
        ])]);
    }

    public function test_finds_animal_by_class_id(): void
    {
        $this->makeTiger();

        $animal = app(FactsheetService::class)->findByClassId(3);

        $this->assertNotNull($animal);
        $this->assertSame('Tiger', $animal->common_name);
    }

    public function test_returns_null_for_unknown_class_id(): void
    {
        $this->assertNull(app(FactsheetService::class)->findByClassId(99));
    }

    public function test_scan_returns_factsheet_for_known_class(): void
    {
        $this->makeTiger();
        $this->fakeAi(3);

        $this->actingAs(User::factory()->create())
            ->postJson('/scan', ['image' => UploadedFile::fake()->image('foto.jpg')])
            ->assertOk()
            ->assertJsonPath('status', 'success')
            ->assertJsonPath('detections.0.animal.common_name', 'Tiger');
    }

    public function test_scan_returns_422_when_animal_missing(): void
    {
        $this->fakeAi(99);

        $this->actingAs(User::factory()->create())
            ->postJson('/scan', ['image' => UploadedFile::fake()->image('foto.jpg')])
            ->assertStatus(422)
            ->assertJsonPath('status', 'error')
            ->assertJsonPath('code', 'no_animal_detected');
    }
}