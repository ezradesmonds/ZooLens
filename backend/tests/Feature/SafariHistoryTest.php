<?php

namespace Tests\Feature;

use App\Models\Animal;
use App\Models\Detection;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class SafariHistoryTest extends TestCase
{
    use RefreshDatabase;

    private function makeAnimal(int $classId, string $name): Animal
    {
        return Animal::create([
            'class_id' => $classId,
            'common_name' => $name,
            'scientific_name' => 'test',
            'habitat' => 'test',
            'diet' => 'test',
            'iucn_status' => 'LC',
        ]);
    }

    public function test_safari_shows_progress_for_logged_in_user(): void
    {
        $user = User::factory()->create();
        $elephant = $this->makeAnimal(0, 'Elephant');
        $this->makeAnimal(1, 'Giraffe');
        $user->animals()->attach($elephant->id, ['discovered_at' => now()]);

        $this->actingAs($user)
            ->get('/safari')
            ->assertOk()
            ->assertViewHas('total', 2)
            ->assertViewHas('unlocked', 1)
            ->assertViewHas('percent', 50);
    }

    public function test_history_only_shows_own_detections(): void
    {
        $me = User::factory()->create();
        $other = User::factory()->create();
        $elephant = $this->makeAnimal(0, 'Elephant');

        $base = [
            'animal_id' => $elephant->id,
            'confidence' => 0.9,
            'bbox_x1' => 1, 'bbox_y1' => 1, 'bbox_x2' => 2, 'bbox_y2' => 2,
            'image_width' => 100, 'image_height' => 100,
        ];
        Detection::create($base + ['user_id' => $me->id]);
        Detection::create($base + ['user_id' => $other->id]);

        $this->actingAs($me)
            ->get('/history')
            ->assertOk()
            ->assertViewHas('histories', fn ($h) => count($h) === 1);
    }

    public function test_guest_cannot_open_safari_or_history(): void
    {
        $this->get('/safari')->assertRedirect('/login');
        $this->get('/history')->assertRedirect('/login');
    }
}