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

#ifndef CONTROL_SET_H
#define CONTROL_SET_H

#include <QHash>
#include <QSharedPointer>
#include <QUuid>
#include <QWeakPointer>

class Control;
class Executor;

class ControlSet {
private:
  QWeakPointer<Executor> m_executor;
  QHash<QUuid, QSharedPointer<Control>> m_controls;

public:
  ControlSet(const QWeakPointer<Executor> &executor);

  QSharedPointer<Control> create(const QString &c);
  bool destroy(const QUuid &i, bool force);
  bool contains(const QUuid &i);
  QList<QSharedPointer<Control>> list();
  QSharedPointer<Control> find(const QUuid &i);
};

#endif // CONTROL_SET_H
