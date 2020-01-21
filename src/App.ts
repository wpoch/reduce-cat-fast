#!/usr/bin/env node

import * as prog from 'caporal';
import { Capturer } from './Capturer';

prog
    .version('0.0.1')
    .command('capture', 'Capture raw cat pictures')
    .option('--output <output>', 'Output folder of the captures', prog.STRING, './to-classify')
    .action(async (_, options, logger) => {
        await new Capturer(options.output, {logger}).execute();
    });

prog.parse(process.argv);
