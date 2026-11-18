<?php

namespace Tests\Feature;

use App\Models\Animal;
use App\Models\User;
use App\Services\CollectionService;
use Database\Seeders\AnimalSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class CollectionProgressTest extends TestCase
{
    use RefreshDatabase;

    private function detection(int $classId, float $confidence = 0.9): array
    {
        return [
            'class_id' => $classId,
            'confidence' => $confidence,
            'bbox' => [10, 20, 300, 400],
        ];
    }

    private function scan(User $user, int $classId, float $confidence = 0.9): array
    {
        $animal = Animal::where('class_id', $classId)->firstOrFail();

        return app(CollectionService::class)->record(
            $user,
            $animal,
            $this->detection($classId, $confidence),
            1280,
            960
        );
    }

    public function test_progress_starts_at_zero(): void
    {
        $this->seed(AnimalSeeder::class);
        $user = User::factory()->create();

        $progress = app(CollectionService::class)->progress($user);

        $this->assertSame(0, $progress['collected']);
        $this->assertSame(5, $progress['total']);
        $this->assertEquals(0, $progress['percentage']);
    }

    public function test_progress_counts_unique_animals_and_percentage(): void
    {
        $this->seed(AnimalSeeder::class);
        $user = User::factory()->create();

        $this->scan($user, 0);
        $this->scan($user, 3);

        $progress = app(CollectionService::class)->progress($user);

        $this->assertSame(2, $progress['collected']);
        $this->assertSame(5, $progress['total']);
        $this->assertEquals(40, $progress['percentage']);
    }

    public function test_same_animal_twice_does_not_increase_progress(): void
    {
        $this->seed(AnimalSeeder::class);
        $user = User::factory()->create();

        $first = $this->scan($user, 0);
        $second = $this->scan($user, 0);

        $this->assertTrue($first['is_new_discovery']);
        $this->assertFalse($second['is_new_discovery']);
        $this->assertSame(1, app(CollectionService::class)->progress($user)['collected']);
    }

    public function test_progress_is_separate_per_user(): void
    {
        $this->seed(AnimalSeeder::class);
        $userA = User::factory()->create();
        $userB = User::factory()->create();

        $this->scan($userA, 0);

        $this->assertSame(1, app(CollectionService::class)->progress($userA)['collected']);
        $this->assertSame(0, app(CollectionService::class)->progress($userB)['collected']);
    }

    public function test_first_discovery_returns_badge_with_name_and_icon(): void
    {
        $this->seed(AnimalSeeder::class);
        $user = User::factory()->create();

        $outcome = $this->scan($user, 1);

        $this->assertTrue($outcome['is_new_discovery']);
        $this->assertNotNull($outcome['badge']);
        $this->assertArrayHasKey('name', $outcome['badge']);
        $this->assertArrayHasKey('icon', $outcome['badge']);
    }

    public function test_low_confidence_does_not_change_progress(): void
    {
        $this->seed(AnimalSeeder::class);
        $user = User::factory()->create();

        $outcome = $this->scan($user, 2, 0.3);

        $this->assertFalse($outcome['is_new_discovery']);
        $this->assertSame(0, app(CollectionService::class)->progress($user)['collected']);
    }

    public function test_progress_does_not_crash_when_there_are_no_animals(): void
    {
        $user = User::factory()->create();

        $progress = app(CollectionService::class)->progress($user);

        $this->assertSame(0, $progress['total']);
        $this->assertEquals(0, $progress['percentage']);
    }
}