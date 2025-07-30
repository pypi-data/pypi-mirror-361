/*
 * Copyright 2023 Yunseong Hwang
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef SHOW_MESSAGE_H
#define SHOW_MESSAGE_H

#include <qstring.h>
#include <qtconfigmacros.h>

QT_BEGIN_NAMESPACE

enum MessageType {
  DebugMessage,
  InfoMessage,
  WarningMessage,
  CriticalMessage,
  FatalMessage,
};

void showMessage(const QString &message, MessageType type);

QT_END_NAMESPACE

#endif // SHOW_MESSAGE_H
