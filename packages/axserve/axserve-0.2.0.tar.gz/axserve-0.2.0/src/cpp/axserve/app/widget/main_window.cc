// Copyright 2023 Yunseong Hwang
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// SPDX-License-Identifier: Apache-2.0

#include "main_window.h"

#include <QCoreApplication>
#include <QStyle>
#include <QTimer>

MainSystemTrayIconMenu::MainSystemTrayIconMenu(
    MainWindow *main, QWidget *parent
)
    : QMenu(parent),
      m_main(main) {
  m_restoreAction = addAction(tr("Restore"));
  m_exitAction = addAction(tr("Exit"));
  connect(
      m_restoreAction, &QAction::triggered, m_main, &MainWindow::showRaised
  );
  connect(
      m_exitAction, &QAction::triggered, QCoreApplication::instance(),
      &QCoreApplication::quit, Qt::QueuedConnection
  );
  setStyleSheet("QMenu::item { padding: 10px 20px; }");
}

MainSystemTrayIcon::MainSystemTrayIcon(MainWindow *main, QObject *parent)
    : QSystemTrayIcon(parent),
      m_main(main) {
  m_icon = m_main->windowIcon();
  m_menu = new MainSystemTrayIconMenu(m_main, m_main);
  setIcon(m_icon);
  setContextMenu(m_menu);
  connect(
      this, &QSystemTrayIcon::activated, this, &MainSystemTrayIcon::activate
  );
}

void MainSystemTrayIcon::activate(QSystemTrayIcon::ActivationReason reason) {
  switch (reason) {
  case QSystemTrayIcon::DoubleClick: {
    m_main->showRaised();
    break;
  }
  }
}
MainWindow::MainWindow(
    ParsedConfig config, QWidget *parent, Qt::WindowFlags flags
)
    : QMainWindow(parent, flags),
      m_config(std::move(config)) {
  m_icon = style()->standardIcon(QStyle::StandardPixmap::SP_TitleBarMenuButton);
  setWindowIcon(m_icon);
  m_trayIcon = new MainSystemTrayIcon(this, this);
  if (m_config.trayIcon) {
    m_trayIcon->show();
  }
}

void MainWindow::showRaised() {
  if (isMinimized() || !isVisible()) {
    showNormal();
  }
  raise();
  activateWindow();
}

void MainWindow::closeEvent(QCloseEvent *event) {
  if (event && !event->spontaneous())
    return;
  if (!isVisible())
    return;
  if (m_config.hideOnClose) {
    hide();
    m_trayIcon->showMessage(
        tr("Window is currently hidden."),
        tr("Double click tray icon to reopen the window.")
    );
    event->ignore();
  }
}

void MainWindow::changeEvent(QEvent *event) {
  if (m_config.hideOnMinimize && event->type() == QEvent::WindowStateChange &&
      isMinimized()) {
    QTimer::singleShot(0, this, &QWidget::hide);
  }
  QMainWindow::changeEvent(event);
}

/*
void MainWindow::onInitialStartRequest(const StartServerConfiguration &conf) {
  // pass initial values to edits
  m_start->onInitialStartRequest(conf);

  // check gui availability
  bool noGui = QCoreApplication::instance()
      ? QCoreApplication::instance()->property("noGui").toBool()
      : false;

  // show main window if needed
  if (!noGui && !conf.startHidden()) {
    showNormal();
  }

  // try start if possible
  if (!conf.address().isEmpty()) {
    if (!m_start->onStartButtonClick()) {
      if (noGui) {
        ::exit(EXIT_FAILURE);
      } else if (!isVisible()) {
        showNormal();
      }
    }
  }
}

void MainWindow::onStartRequest(const StartServerConfiguration &conf) {
  qDebug() << "Starting server with clsid:" << conf.controls()
           << "and address:" << conf.addresses();

  RunningServerWidget *running =
      new RunningServerWidget(conf.controls(), conf.addresses(), this);

  if (!running->isReady()) {
    // check gui availability and app title for printing errors
    QCoreApplication *app = QCoreApplication::instance();
    bool noGui = false;
    QString title;
    if (app)
      noGui = app->property("noGui").toBool();
    if (!noGui) {
      if (app)
        title = app->property("applicationDisplayName").toString();
      if (title.isEmpty()) {
        title = QCoreApplication::applicationName();
      }
    }

    // print error based on failed reason
    switch (running->failedReason()) {
    case RunningServerWidget::FailedReason::CONTROL: {
      QString message = tr("Failed to initialize COM/OCX for the given CLSID.");
      qCritical() << qPrintable(message);
      if (!noGui) {
        QMessageBox msgBox;
        msgBox.setIcon(QMessageBox::Critical);
        msgBox.setWindowTitle(title);
        msgBox.setText(message);
        msgBox.exec();
      }
      if (noGui) {
        ::exit(EXIT_FAILURE);
      } else if (!isVisible()) {
        showNormal();
      }
      break;
    }
    case RunningServerWidget::FailedReason::SERVER: {
      QString message =
          tr("Failed to start server, possibly due to the invalid address "
             "given.");
      qCritical() << qPrintable(message);
      if (!noGui) {
        QMessageBox msgBox;
        msgBox.setIcon(QMessageBox::Critical);
        msgBox.setWindowTitle(title);
        msgBox.setText(message);
        msgBox.exec();
      }
      if (noGui) {
        ::exit(EXIT_FAILURE);
      } else if (!isVisible()) {
        showNormal();
      }
      break;
    }
    default: {
      QString message = tr("Failed to start server, for unknown reason.");
      qCritical() << qPrintable(message);
      if (!noGui) {
        QMessageBox msgBox;
        msgBox.setIcon(QMessageBox::Critical);
        msgBox.setWindowTitle(title);
        msgBox.setText(message);
        msgBox.exec();
      }
      if (noGui) {
        ::exit(EXIT_FAILURE);
      } else if (!isVisible()) {
        showNormal();
      }
      break;
    }
    }

    // delete invalid running widget
    running->deleteLater();
  } else {
    // add successful values to edit history
    auto address = conf.address();
    auto controls = conf.controls();

    // add and set running widget as current widget
    m_running = running;
    m_central->addWidget(running);
    m_central->setCurrentWidget(running);

    // create tray icon if needed
    if (conf.createTrayIcon()) {
      m_trayIcon->show();
      m_trayIcon->setToolTip(address);
    }

    // minimize or hide if needed
    if (isVisible() && m_trayIcon->isVisible() && conf.startHidden()) {
      hide();
    }
  }
}
*/
