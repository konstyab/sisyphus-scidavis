/***************************************************************************
    File                 : String2DoubleFilter.h
    Project              : SciDAVis
    --------------------------------------------------------------------
    Copyright            : (C) 2007 by Knut Franke
    Email (use @ for *)  : knut.franke*gmx.de
    Description          : Locale-aware conversion filter QString -> double.
                           
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *  This program is free software; you can redistribute it and/or modify   *
 *  it under the terms of the GNU General Public License as published by   *
 *  the Free Software Foundation; either version 2 of the License, or      *
 *  (at your option) any later version.                                    *
 *                                                                         *
 *  This program is distributed in the hope that it will be useful,        *
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of         *
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          *
 *  GNU General Public License for more details.                           *
 *                                                                         *
 *   You should have received a copy of the GNU General Public License     *
 *   along with this program; if not, write to the Free Software           *
 *   Foundation, Inc., 51 Franklin Street, Fifth Floor,                    *
 *   Boston, MA  02110-1301  USA                                           *
 *                                                                         *
 ***************************************************************************/
#ifndef STRING2DOUBLE_FILTER_H
#define STRING2DOUBLE_FILTER_H

#include "../AbstractSimpleFilter.h"
#include <QLocale>
#include "lib/XmlStreamReader.h"
#include <QXmlStreamWriter>
#include <QtDebug>

//! Locale-aware conversion filter QString -> double.
class String2DoubleFilter : public AbstractSimpleFilter
{
	Q_OBJECT

	public:
		String2DoubleFilter() : d_use_default_locale(true) {}
		void setNumericLocale(QLocale locale) { d_numeric_locale = locale; d_use_default_locale = false; }
		void setNumericLocaleToDefault() { d_use_default_locale = true; }

		virtual double valueAt(int row) const {
			if (!d_inputs.value(0)) return 0;
			if (d_use_default_locale) // we need a new QLocale instance here in case the default changed since the last call
				return QLocale().toDouble(d_inputs.value(0)->textAt(row));
			return d_numeric_locale.toDouble(d_inputs.value(0)->textAt(row));
		}
		virtual bool isInvalid(int row) const { 
			if (!d_inputs.value(0)) return false;
			bool ok;
			if (d_use_default_locale)
				QLocale().toDouble(d_inputs.value(0)->textAt(row), &ok);
			else
				d_numeric_locale.toDouble(d_inputs.value(0)->textAt(row), &ok);
			return !ok;
		}
		virtual bool isInvalid(Interval<int> i) const {
			if (!d_inputs.value(0)) return false;
			QLocale locale;
			if (!d_use_default_locale)
				locale = d_numeric_locale;
			for (int row = i.start(); row <= i.end(); row++) {
				bool ok;
				locale.toDouble(d_inputs.value(0)->textAt(row), &ok);
				if (ok)
					return false;
			}
			return true;
		}
		virtual QList< Interval<int> > invalidIntervals() const 
		{
			IntervalAttribute<bool> validity;
			if (d_inputs.value(0)) {
				int rows = d_inputs.value(0)->rowCount();
				for (int i=0; i<rows; i++) 
					validity.setValue(i, isInvalid(i));
			}
			return validity.intervals();
		}


		//! Return the data type of the column
		virtual SciDAVis::ColumnDataType dataType() const { return SciDAVis::TypeDouble; }

	protected:
		//! Using typed ports: only string inputs are accepted.
		virtual bool inputAcceptable(int, const AbstractColumn *source) {
			return source->dataType() == SciDAVis::TypeQString;
		}

	private:
		QLocale d_numeric_locale;
		bool d_use_default_locale;
};

#endif // ifndef STRING2DOUBLE_FILTER_H

