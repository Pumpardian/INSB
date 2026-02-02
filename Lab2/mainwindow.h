#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include "textEncryption.h"
#include <QMessageBox>
#include <QFileDialog>
#include <QFile>
#include <QTextStream>

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private:
    Ui::MainWindow *ui;
    EncryptableText *text;

    bool validateKeyword();

private slots:
    void on_encryptCaesar_pushButton_clicked();
    void on_decryptCaesar_pushButton_clicked();

    void on_encryptVegener_pushButton_clicked();
    void on_decryptVegener_pushButton_clicked();

    void on_loadUnencrypted_pushButton_clicked();
    void on_saveUnencrypted_pushButton_clicked();

    void on_loadEncrypted_pushButton_clicked();
    void on_saveEncrypted_pushButton_clicked();
};

#endif // MAINWINDOW_H