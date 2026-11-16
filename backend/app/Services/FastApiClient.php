<?php

namespace App\Services;

use App\Exceptions\AiServiceException;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Http;

class FastApiClient
{
    /**
     * Kirim gambar ke FastAPI /predict dan kembalikan hasilnya (sudah divalidasi).
     *
     * @throws AiServiceException jika FastAPI tidak bisa dihubungi, membalas error,
     *                            atau bentuk responsnya tidak sesuai kontrak.
     */
    public function predict(UploadedFile $file): array
    {
        $baseUrl = rtrim(config('services.ai.url', 'http://127.0.0.1:8001'), '/');
        $timeout = (int) config('services.ai.timeout', 10);

        try {
            $response = Http::timeout($timeout)
                ->attach('file', file_get_contents($file->getRealPath()), $file->getClientOriginalName())
                ->post($baseUrl . '/predict');
        } catch (ConnectionException $e) {
            throw new AiServiceException('FastAPI tidak bisa dihubungi: ' . $e->getMessage(), 0, $e);
        }

        if (! $response->successful()) {
            throw new AiServiceException('FastAPI membalas HTTP ' . $response->status());
        }

        return $this->validated($response->json());
    }

    private function validated(mixed $data): array
    {
        if (! is_array($data)
            || ! isset($data['image_width'], $data['image_height'], $data['detections'])
            || ! is_numeric($data['image_width'])
            || ! is_numeric($data['image_height'])
            || ! is_array($data['detections'])
        ) {
            throw new AiServiceException('Respons FastAPI tidak sesuai kontrak.');
        }

        foreach ($data['detections'] as $detection) {
            if (! is_array($detection)
                || ! isset($detection['class_id'], $detection['confidence'], $detection['bbox'])
                || ! is_numeric($detection['class_id'])
                || ! is_numeric($detection['confidence'])
                || ! is_array($detection['bbox'])
                || count($detection['bbox']) !== 4
            ) {
                throw new AiServiceException('Isi deteksi dari FastAPI tidak sesuai kontrak.');
            }
        }

        return $data;
    }
}