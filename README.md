# Pressure Sensor Notification System

## TODO
- [x] Make web dashboard
- [x] Test router
- [x] Delete and move all credentials and private resource to private file (ignored from git)
- [x] Refactor modbus calculation in python
- [x] Setup better development environment
- [x] Integration available zone and rules with database
- [x] Move telegram call API to python
- [x] Retest website with new python API
- [ ] Add loading state when submit
- [ ] Add nginx and basic auth
- [ ] Add auto run python script
- [ ] Setup open vpn
- [ ] (Optional) Test multiple modbus connection

## Question

- Apakah satu microcontroller untuk satu sensor ? Perlu uji coba lebih lanjut jika ingin menggunakan satu microcontroller untuk beberapa sensor
- Apakah perlu simple dashboard website yang di simpan dalam microcontroller (tanpa server) agar user bisa mengubah rules set point tiap alat dan menambars485h alat baru? Jika tidak configurasi alat bisa dilakukan dengan merubah code arduino kemudian mengupload ulang
- Bagaimana bentuk notifikasi yang diharapkan ? Apakah cukup sekali notifikasi (Cons: tidak mengetahui kapan tekananannya turun) ? atau setiap beberapa detik ketika ada tekanan berlebih (akan spam message)
- Kemungkinan membutuhkan notifikasi berkala (mungkin setiap jam) untuk memastikan sistem notifikasi masih berjalan

## Panduan Penggunaan Website

### Pengisian Kolom:

Semua kolom wajib diisi.

- Nilai Min dan Max harus berupa angka.
- Nilai Max harus lebih besar dari Min.
- Format Nama Ruangan:
  Disarankan untuk menggunakan format berikut pada Room Name:
  - Ruang #[lantai]0[ruang]. Contoh: Ruang #102 berarti lantai 1, ruang 2.

- Menyimpan Konfigurasi:
  Klik Save untuk menyimpan konfigurasi yang telah diisi. Lalu lakukan refresh halaman.

- Edit dan Hapus Data:
  Anda dapat mengedit atau menghapus data tanpa perlu me-refresh lagi.
