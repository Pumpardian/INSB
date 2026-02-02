#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    text = new EncryptableText();
}

MainWindow::~MainWindow()
{
    delete text;
    delete ui;
}

void MainWindow::on_encryptCaesar_pushButton_clicked()
{
    if (ui->shift_spinBox->value() == 0)
    {
        QMessageBox::information(nullptr, "?", "What is even the point of crypting/decrypting?", QMessageBox::Ok);
        return;
    }
    QString crypted = text->EncryptCaesar(ui->shift_spinBox->value(), ui->unencrypted_plainTextEdit->toPlainText());
    ui->encrypted_plainTextEdit->setPlainText(crypted);
}

void MainWindow::on_decryptCaesar_pushButton_clicked()
{
    if (ui->shift_spinBox->value() == 0)
    {
        QMessageBox::information(nullptr, "?", "What is even the point of crypting/decrypting?", QMessageBox::Ok);
        return;
    }
    QString decrypted = text->DecryptCaesar(ui->shift_spinBox->value(), ui->encrypted_plainTextEdit->toPlainText());
    ui->unencrypted_plainTextEdit->setPlainText(decrypted);
}

void MainWindow::on_encryptVegener_pushButton_clicked()
{
    if (!validateKeyword())
    {
        return;
    }

    QString crypted = text->EncryptVegener(ui->word_lineEdit->text().trimmed(), ui->unencrypted_plainTextEdit->toPlainText());
    ui->encrypted_plainTextEdit->setPlainText(crypted);
}

void MainWindow::on_decryptVegener_pushButton_clicked()
{
    if (!validateKeyword())
    {
        return;
    }

    QString decrypted = text->DecryptVegener(ui->word_lineEdit->text(), ui->encrypted_plainTextEdit->toPlainText());
    ui->unencrypted_plainTextEdit->setPlainText(decrypted);
}

void MainWindow::on_loadUnencrypted_pushButton_clicked()
{
    QString fileName = QFileDialog::getOpenFileName(nullptr, tr("Load"), "unencrypted.txt", tr("TXT (*.txt)"));
    if (fileName.isEmpty())
        return;

    QFile file(fileName);

    if (file.open(QIODevice::ReadOnly) | QIODevice::Text)
    {
        QTextStream in(&file);
        QString content = in.readAll();
        ui->unencrypted_plainTextEdit->setPlainText(content);
        file.close();
    }
    else
    {
        QMessageBox::critical(nullptr, "Load", "Error while opening file", QMessageBox::Ok);
    }
}

void MainWindow::on_saveUnencrypted_pushButton_clicked()
{
    QString fileName = QFileDialog::getSaveFileName(nullptr, tr("Save"), "unencrypted.txt", tr("TXT (*.txt)"));
    if (fileName.isEmpty())
        return;

    QFile file(fileName);

    if (file.open(QIODevice::WriteOnly) | QIODevice::Text | QIODevice::Truncate)
    {
        QTextStream out(&file);
        out << ui->unencrypted_plainTextEdit->toPlainText();
        file.close();
    }
    else
    {
        QMessageBox::critical(nullptr, "Save", "Error while saving file", QMessageBox::Ok);
    }
}

void MainWindow::on_loadEncrypted_pushButton_clicked()
{
    QString fileName = QFileDialog::getOpenFileName(nullptr, tr("Load"), "encrypted.txt", tr("TXT (*.txt)"));
    if (fileName.isEmpty())
        return;

    QFile file(fileName);

    if (file.open(QIODevice::ReadOnly) | QIODevice::Text)
    {
        QTextStream in(&file);
        QString content = in.readAll();
        ui->encrypted_plainTextEdit->setPlainText(content);
        file.close();
    }
    else
    {
        QMessageBox::critical(nullptr, "Load", "Error while opening file", QMessageBox::Ok);
    }
}

void MainWindow::on_saveEncrypted_pushButton_clicked()
{
    QString fileName = QFileDialog::getSaveFileName(nullptr, tr("Save"), "encrypted.txt", tr("TXT (*.txt)"));
    if (fileName.isEmpty())
        return;

    QFile file(fileName);

    if (file.open(QIODevice::WriteOnly) | QIODevice::Text | QIODevice::Truncate)
    {
        QTextStream out(&file);
        out << ui->encrypted_plainTextEdit->toPlainText();
        file.close();
    }
    else
    {
        QMessageBox::critical(nullptr, "Save", "Error while saving file", QMessageBox::Ok);
    }
}

bool MainWindow::validateKeyword()
{
    int length = 0;

    if (ui->word_lineEdit->text().trimmed().isNull())
    {
        QMessageBox::warning(nullptr, "Keyword warning", "Keyword is empty", QMessageBox::Ok);
        return false;
    }

    for (auto &c : ui->word_lineEdit->text().trimmed())
    {
        for (auto &alphabet : text->alphabets)
        {
            if (alphabet.contains(c, Qt::CaseInsensitive))
            {
                ++length;
                break;
            }
        }
    }
    
    if (length != ui->word_lineEdit->text().trimmed().length())
    {
        QMessageBox::warning(nullptr, "Keyword warning", "Keyword contains symbols that are out of known alpabets, please provide another keyword", QMessageBox::Ok);
        return false;
    }

    return true;
}