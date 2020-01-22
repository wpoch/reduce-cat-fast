import * as tf from '@tensorflow/tfjs-node';

interface ICapturerOptons {
    logger: Logger
}
export class Capturer {
    output: String;

    logger: Logger;

    constructor(output: String, options : ICapturerOptons) {
        this.output = output;
        this.logger = options.logger;
    }

    execute(): Promise<void> {
        this.logger.info(`Capturer`, this.output);
        return new Promise<void>(() => {
        });
    }
}
