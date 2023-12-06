Use emojis in log messages.

Use single quotes instead of double quotes for strings whenever possible.

Use a lot of log messages, almost every line, if possible.



this would be better:


* Use emojis in log messages.
* Use single quotes instead of double quotes for strings whenever possible.
* Use a lot of log messages, almost every line, if possible.
* For log messages, when you're saying what is about to be done, end the log message with ellipses. When the operation is done, end it with a period.
* For log messages, when you're saying what is about to be done, end the log message with ellipses. When the operation is done, end it with a period. Additionally, when a new variable is made or data is changed or updated, add a log debug statement discussing it, and printing it out appropriately. For instance, instead of:
```
logging.info('📊 Performing histogram equalization...')
equalized_image = exposure.equalize_hist(greyscale_imag
```
this would have been better:
```
logging.debug(f'📊 Histogram before equalization: {exposure.histogram(greyscale_image)[0] = }')
logging.info('📊 Performing histogram equalization...')
equalized_image = exposure.equalize_hist(greyscale_image)
logging.debug(f'📊 Histogram after equalization: {exposure.histogram(equalized_image)[0] = }')
```
* As noted above, when possible use f-strings like logging.debug(f'📝 {dataframe.columns = }') instead of logging.debug(f'📝 Columns = {dataframe.columns}')
* Value DRY principle. Value deduplication - if a value is used more than once, modularize it.
* Make variable names long and descriptive, full words connected by underscores if possible, preferring self-documenting code over comments.
* Prefer two linebreaks between functions.
* Always try to deduplicate and abstract away commonalities (e.g. variable names, prefixes and suffixes for strings, etc.). For instance:
```
X = ['Val1', 'Val2', 'Val3']
```
should really be
```
X = [f'Val{i}' for i in range(1,4)]
```
Also, for instance,
```
preTx_SHIM = df['PreTx SHIM'].values
month_6_SHIM = df['6 month SHIM'].values
month_12_SHIM = df['12 month SHIM'].values
month_24_SHIM = df['24 month SHIM'].values
```
would be better as:
```
SHIM_values = {time_period: df[f'{time_period} SHIM'] for time_period in ['PreTx'] + [f'{x} month' for x in [6,12,24]]}
```
because nothing is duplicated and now we have a dictionary with keys and values for easier use, instead of relying on variable names.
