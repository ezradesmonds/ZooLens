<?php

namespace Tests\Feature;

use App\Exceptions\AiServiceException;
use App\Models\User;
use App\Services\FastApiClient;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Http;
use Tests\TestCase;

class FastApiClientTest extends TestCase
{
    use RefreshDatabase;

    private function validPayload(): array
    {
        return [
            'image_width' => 1280,
            'image_height' => 960,
            'detections' => [
                ['class_id' => 0, 'class_name' => 'elephant', 'confidence' => 0.92, 'bbox' => [10, 20, 300, 400]],
            ],
        ];
    }

    public function test_predict_returns_validated_result(): void
    {
        Http::fake(['*' => Http::response($this->validPayload())]);

        $result = app(FastApiClient::class)->predict(UploadedFile::fake()->image('foto.jpg'));

        $this->assertSame(1280, $result['image_width']);
        $this->assertSame(0, $result['detections'][0]['class_id']);
    }

    public function test_predict_accepts_empty_detections(): void
    {
        Http::fake(['*' => Http::response(['image_width' => 100, 'image_height' => 100, 'detections' => []])]);

        $result = app(FastApiClient::class)->predict(UploadedFile::fake()->image('foto.jpg'));

        $this->assertSame([], $result['detections']);
    }

    public function test_predict_throws_when_connection_fails(): void
    {
        Http::fake(function () {
            throw new ConnectionException('Connection refused');
        });

        $this->expectException(AiServiceException::class);

        app(FastApiClient::class)->predict(UploadedFile::fake()->image('foto.jpg'));
    }

    public function test_predict_throws_when_fastapi_returns_error_status(): void
    {
        Http::fake(['*' => Http::response(['detail' => 'Model not installed'], 503)]);

        $this->expectException(AiServiceException::class);

        app(FastApiClient::class)->predict(UploadedFile::fake()->image('foto.jpg'));
    }

    public function test_predict_throws_when_response_shape_is_invalid(): void
    {
        Http::fake(['*' => Http::response(['foo' => 'bar'])]);

        $this->expectException(AiServiceException::class);

        app(FastApiClient::class)->predict(UploadedFile::fake()->image('foto.jpg'));
    }

    public function test_scan_returns_503_when_fastapi_response_is_invalid(): void
    {
        Http::fake(['*' => Http::response(['foo' => 'bar'])]);

        $this->actingAs(User::factory()->create())
            ->postJson('/scan', ['image' => UploadedFile::fake()->image('foto.jpg')])
            ->assertStatus(503)
            ->assertJsonPath('code', 'ai_unavailable');
    }
}