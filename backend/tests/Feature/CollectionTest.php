<?php

namespace Tests\Feature;

use App\Models\Animal;
use App\Models\Badge;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Http;
use Tests\TestCase;

class CollectionTest extends TestCase
{
    use RefreshDatabase;

    private function makeTiger(): Animal
    {
        $animal = Animal::create([
            'class_id' => 3,
            'common_name' => 'Tiger',
            'scientific_name' => 'Panthera tigris',
            'habitat' => 'test',
            'diet' => 'test',
            'iucn_status' => 'EN',
        ]);

        Badge::create([
            'animal_id' => $animal->id,
            'name' => 'Lencana Tiger',
            'description' => 'test',
            'icon' => 'tiger.png',
        ]);

        return $animal;
    }

    private function fakeAi(float $confidence): void
    {
        Http::fake(['*' => Http::response([
            'image_width' => 1280,
            'image_height' => 960,
            'detections' => [
                ['class_id' => 3, 'confidence' => $confidence, 'bbox' => [100, 80, 300, 260]],
            ],
        ])]);
    }

    private function scan(User $user)
    {
        return $this->actingAs($user)
            ->postJson('/scan', ['image' => UploadedFile::fake()->image('foto.jpg')]);
    }

    public function test_confident_detection_is_saved_and_collected(): void
    {
        $user = User::factory()->create();
        $animal = $this->makeTiger();
        $this->fakeAi(0.91);

        $this->scan($user)
            ->assertOk()
            ->assertJsonPath('detections.0.is_new_discovery', true)
            ->assertJsonPath('detections.0.badge.name', 'Lencana Tiger')
            ->assertJsonPath('progress.collected', 1)
            ->assertJsonPath('progress.percentage', 100);

        $this->assertDatabaseHas('detections', ['user_id' => $user->id, 'animal_id' => $animal->id]);
        $this->assertDatabaseHas('user_animals', ['user_id' => $user->id, 'animal_id' => $animal->id]);
    }

    public function test_second_scan_of_same_animal_is_not_new(): void
    {
        $user = User::factory()->create();
        $this->makeTiger();
        $this->fakeAi(0.91);

        $this->scan($user);
        $this->scan($user)
            ->assertJsonPath('detections.0.is_new_discovery', false)
            ->assertJsonPath('detections.0.badge', null);

        $this->assertDatabaseCount('detections', 2);
        $this->assertDatabaseCount('user_animals', 1);
    }

    public function test_low_confidence_is_saved_but_not_collected(): void
    {
        $user = User::factory()->create();
        $this->makeTiger();
        $this->fakeAi(0.30);

        $this->scan($user)
            ->assertOk()
            ->assertJsonPath('detections.0.is_new_discovery', false)
            ->assertJsonPath('progress.collected', 0);

        $this->assertDatabaseCount('detections', 1);
        $this->assertDatabaseCount('user_animals', 0);
    }
}