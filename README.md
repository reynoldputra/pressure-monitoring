# Pressure Sensor Notification System

## TODO

- Delete and move all telegram API to private file (ignored from git)
- Test notification system with Hf2211
- (Optional) Make web dashboard
- (Optional) Test multiple modbus connection

## Question

- Apakah satu microcontroller untuk satu sensor ? Perlu uji coba lebih lanjut jika ingin menggunakan satu microcontroller untuk beberapa sensor
- Apakah perlu simple dashboard website yang di simpan dalam microcontroller (tanpa server) agar user bisa mengubah rules set point tiap alat dan menambah alat baru? Jika tidak configurasi alat bisa dilakukan dengan merubah code arduino kemudian mengupload ulang
- Bagaimana bentuk notifikasi yang diharapkan ? Apakah cukup sekali notifikasi (Cons: tidak mengetahui kapan tekananannya turun) ? atau setiap beberapa detik ketika ada tekanan berlebih (akan spam message)
- Kemungkinan membutuhkan notifikasi berkala (mungkin setiap jam) untuk memastikan sistem notifikasi masih berjalan

## Panduan Penggunaan Website

### 1.Pengisian Kolom:

Semua kolom wajib diisi.

- Nilai Min dan Max harus berupa angka.
- Nilai Max harus lebih besar dari Min.
- Format Nama Ruangan:
  Disarankan untuk menggunakan format berikut pada Room Name: - Ruang #lantai - ruang. Contoh: 101 berarti ruang 1 di lantai 1.

- Menyimpan Konfigurasi:
  Klik Save untuk menyimpan konfigurasi yang telah diisi. Lalu lakukan refresh halaman.

- Edit dan Hapus Data:
  Anda dapat mengedit atau menghapus data tanpa perlu me-refresh lagi.
