* Use emojis in log messages.
* Use single quotes instead of double quotes for strings whenever possible.
* Use a lot of log messages, almost every line, if possible.
* For log messages, when you're saying what is about to be done, end the log message with ellipses. When the operation is done, end it with a period.
* When possible use f-strings like logging.debug(f'📝 {dataframe.columns = }') instead of logging.debug(f'📝 Columns = {dataframe.columns}')
* Value DRY principle. Value deduplication - if a value is used more than once, modularize it.
* Make variable names long and descriptive, full words connected by underscores if possible, preferring self-documenting code over comments.
* Prefer two linebreaks between functions.
