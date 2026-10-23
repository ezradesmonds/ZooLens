<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
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
        $user = User::factory()->create();

        $this->actingAs($user)
            ->postJson('/scan', ['image' => UploadedFile::fake()->image('foto.jpg')])
            ->assertOk();
    }

    public function test_missing_image_is_rejected(): void
    {
        $user = User::factory()->create();

        $this->actingAs($user)
            ->postJson('/scan', [])
            ->assertStatus(422)
            ->assertJsonPath('code', 'invalid_image');
    }

    public function test_non_image_is_rejected(): void
    {
        $user = User::factory()->create();

        $this->actingAs($user)
            ->postJson('/scan', ['image' => UploadedFile::fake()->create('a.pdf', 10, 'application/pdf')])
            ->assertStatus(422)
            ->assertJsonPath('code', 'invalid_image');
    }

    public function test_image_over_2mb_is_rejected(): void
    {
        $user = User::factory()->create();

        $this->actingAs($user)
            ->postJson('/scan', ['image' => UploadedFile::fake()->create('besar.jpg', 3000, 'image/jpeg')])
            ->assertStatus(422)
            ->assertJsonPath('code', 'invalid_image');
    }
}