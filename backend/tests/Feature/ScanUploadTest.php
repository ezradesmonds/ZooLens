<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Http;
use Tests\TestCase;

class ScanUploadTest extends TestCase
{
    use RefreshDatabase;

    public function test_guest_is_redirected_to_login(): void
    {
        $this->post('/scan')->assertRedirect('/login');
    }

    public function test_valid_image_is_accepted(): void
    {
        Http::fake(['*' => Http::response([
            'image_width' => 1280,
            'image_height' => 960,
            'detections' => [],
        ])]);

        $this->actingAs(User::factory()->create())
            ->postJson('/scan', ['image' => UploadedFile::fake()->image('foto.jpg')])
            ->assertOk();
    }

    public function test_missing_image_is_rejected(): void
    {
        $this->actingAs(User::factory()->create())
            ->postJson('/scan', [])
            ->assertStatus(422)
            ->assertJsonPath('code', 'invalid_image');
    }

    public function test_non_image_is_rejected(): void
    {
        $this->actingAs(User::factory()->create())
            ->postJson('/scan', ['image' => UploadedFile::fake()->create('a.pdf', 10, 'application/pdf')])
            ->assertStatus(422)
            ->assertJsonPath('code', 'invalid_image');
    }

    public function test_image_over_8mb_is_rejected(): void
    {
        $this->actingAs(User::factory()->create())
            ->postJson('/scan', ['image' => UploadedFile::fake()->create('besar.jpg', 9000, 'image/jpeg')])
            ->assertStatus(422)
            ->assertJsonPath('code', 'invalid_image');
    }

    public function test_scan_returns_503_when_ai_service_is_down(): void
    {
        Http::fake(['*' => Http::response([], 500)]);

        $this->actingAs(User::factory()->create())
            ->postJson('/scan', ['image' => UploadedFile::fake()->image('foto.jpg')])
            ->assertStatus(503)
            ->assertJsonPath('status', 'error')
            ->assertJsonPath('code', 'ai_unavailable');
    }
}